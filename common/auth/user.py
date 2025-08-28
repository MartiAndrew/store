import re
from uuid import UUID

import jwt
from fastapi import Depends, Request
from loguru import logger
from pydantic import BaseModel, Field, ValidationError, field_validator

from common.auth.auth_constants import ACCESS_TOKEN_TYPE, Language
from common.auth.auth_errors import (
    InvalidTokenError,
    NotAccessTokenError,
    TokensExpiredError,
    UserNotAuthorizedError,
    UserNotInTokensClaimsError,
)
from common.token_cache.token_cache import TokenCacheService

from configuration.settings import settings


class BaseUser(BaseModel):
    """Базовый класс пользователя из запроса."""

    user_id: int | None
    is_auth: bool | None
    jwt: str | None
    uuid: UUID | None
    language: Language = Field(Language.ru)
    device_id: str

    @field_validator("language", mode="before")
    def validate_language(cls, language: str | None) -> Language:  # noqa: N805
        """Валидация языка пользователя.

        :param language: язык пользователя
        :return: язык пользователя
        """
        return Language(language)


class AnonUser(BaseUser):
    """Модель анонимного пользователя."""

    is_auth: bool = False


class User(BaseUser):
    """Моделька юзера из JWT токена."""

    user_id: int
    token_type: str | None
    exp: int | None
    iat: int | None = None
    jti: UUID | None
    rls: str | None = None
    nickname: str | None = None
    uuid: UUID | None
    avatar: str | None = None

    @field_validator("token_type")
    def validate_token_type(cls, token_type: str | None) -> str:  # noqa: N805
        """Валидация типа токена.

        Доступен только один тип токена "access".

        :param token_type: тип токна

        :raises InvalidTokenError: если не передан тип токена.
        :raises NotAccessTokenError: если передан неверный тип токена.

        :return: тип токена
        """
        logger.info(f"validate_token_type Валидация типа токена {token_type}.")
        if token_type is None:
            raise InvalidTokenError("Token has no type")
        if token_type == ACCESS_TOKEN_TYPE:
            return token_type
        raise NotAccessTokenError()

    @field_validator("exp")
    def validate_exp(cls, exp: int | None) -> int:  # noqa: N805
        """Валидация exp.

        :param exp: exp

        :raises InvalidTokenError: если не передан exp time.

        :return: exp
        """
        if exp is not None:
            return exp
        raise InvalidTokenError(message="Token has no 'exp' claim")

    @field_validator("jti")
    def validate_jti(cls, jti: str | None) -> str:  # noqa: N805
        """Валидация jti.

        :param jti: jti

        :raises InvalidTokenError: если не передан jti.

        :return: jti
        """
        if jti is not None:
            return jti
        raise InvalidTokenError(message="Token has no id")

    @field_validator("user_id")
    def validate_user_id(cls, user_id: int | None) -> int:  # noqa: N805
        """Валидация user_id.

        :param user_id: id пользователя

        :raises UserNotInTokensClaimsError: если не передан user_id.

        :return: user_id
        """
        if user_id is not None:
            return user_id
        raise UserNotInTokensClaimsError()


def device_id_from_header(user_agent_header: str) -> str:
    """Device ID устройства из User-Agent хидера.

    :param user_agent_header: Блок User-Agent из заголовка запроса
    :returns: device_id устройства пользователя
    """
    device_regex = re.compile(r"deviceID\s*:\s+(?P<device_id>.+)\sN")

    if not user_agent_header:
        logger.warning(f"Отсутствует строка user_agent: {user_agent_header}")
        return ""

    user_agent = re.search(device_regex, user_agent_header)
    if not user_agent:
        return ""

    return user_agent.group("device_id")


async def user(  # noqa: C901, WPS210
    request: Request,
) -> User | AnonUser:
    """
    Получить инфу о юзере из хедеров авторизации.

    :param request: Request.

    :raises InvalidTokenError: не валидный токен

    :returns: User or None.
    """
    language = request.headers.get("Accept-Language")
    device_id = device_id_from_header(request.headers.get("User-Agent", ""))

    if not (bearer_token := request.headers.get("authorization")):  # noqa: WPS332
        logger.info("Токен авторизации отсутствует.")
        return AnonUser(
            language=Language(language),
            device_id=device_id,
            user_id=None,
            jwt=None,
            uuid=None,
        )

    raw_jwt = bearer_token.replace("Bearer ", "", 1)

    try:
        claims = jwt.decode(
            raw_jwt,
            key=settings.auth.jwt_signing_key,
            algorithms=["HS256", "HS384", "HS512"],
            options={
                "verify_signature": True,
            },
        )
        logger.info(f"Получены claims из токена авторизации {claims}.")
    except (jwt.PyJWTError, TypeError) as exc:
        logger.error(
            f"Wrong JWT signature - {exc}.",
        )
        raise InvalidTokenError(message="Token is invalid or expired")

    try:
        user = User(
            language=Language(language),
            jwt=raw_jwt,
            device_id=device_id,
            is_auth=None,
            **claims,
        )
    except ValidationError as exp:
        try:  # noqa: WPS505
            logger.error(f"Получен токен с невалидными данными: {exp}")
        except AttributeError as atr_exp:
            logger.info(f"{atr_exp}")
        raise InvalidTokenError(message="Token is invalid or expired")
    return user


async def user_checked_authorization(
    user: User | AnonUser = Depends(user),
    token_cache_service: TokenCacheService = Depends(),
) -> User | AnonUser:
    """Проверяем авторизацию пользователя и добавляем флаг is_auth.

    :param user: пользователь или None
    :param token_cache_service: сервис кеша токенов

    :raises TokensExpiredError: если токен пользователя просрочен

    :returns: Пользователь с флагом авторизации.
    """
    if isinstance(user, AnonUser):
        logger.info("Запрос поступил от анонимного пользователя.")
        return user

    is_auth = bool(await token_cache_service.is_jwt_cached(str(user.jti.hex)))  # type: ignore  # noqa: E501
    if is_auth:
        logger.info(f"Пользователь {user.user_id} авторизован.")
        user.is_auth = is_auth
        return user
    logger.info(f"Пользователь {user.user_id} не авторизован.")
    raise TokensExpiredError()


async def authorized_user(
    user_checked: User | AnonUser = Depends(user_checked_authorization),
) -> User:
    """Получение авторизованного пользователя.

    :param user_checked: пользователь или анонимный

    :raises UserNotAuthorizedError: если пользователя не авторизован

    :returns: Пользователь с флагом авторизации.
    """
    if isinstance(user_checked, AnonUser):
        raise UserNotAuthorizedError

    return user_checked
