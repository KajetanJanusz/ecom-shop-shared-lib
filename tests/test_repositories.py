import uuid

import pytest
from pydantic import BaseModel

from models import User
from shared.exceptions.custom import NotFoundError
from shared.repositories.base import ModelFields


class CreateUserSchema(BaseModel):
    username: str
    email: str


class TestAsyncBaseRepository:
    async def test_create_when_valid_schema_returns_persisted_user(
        self, user_repository
    ):
        # Arrange
        schema = CreateUserSchema(username="alice", email="alice@example.com")

        # Act
        user = await user_repository.create(schema=schema)

        # Assert
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert isinstance(user.id, uuid.UUID)

    async def test_get_one_when_user_exists_returns_correct_user(self, user_repository):
        # Arrange
        created_user = await user_repository.create(
            CreateUserSchema(username="alice", email="alice@example.com")
        )

        # Act
        user = await user_repository.get_one(
            [ModelFields(field=User.id, value=created_user.id)]
        )

        # Assert
        assert user.id == created_user.id
        assert user.username == "alice"

    async def test_get_one_when_not_found_raises_not_found_error(self, user_repository):
        # Arrange
        nonexistent_id = uuid.uuid4()

        # Act & Assert
        with pytest.raises(NotFoundError):
            await user_repository.get_one(
                [ModelFields(field=User.id, value=nonexistent_id)]
            )

    async def test_get_many_returns_all_users(self, user_repository):
        # Arrange
        await user_repository.create(
            CreateUserSchema(username="carol", email="carol@example.com")
        )
        await user_repository.create(
            CreateUserSchema(username="dave", email="dave@example.com")
        )

        # Act
        users = await user_repository.get_many()

        # Assert
        assert len(users) == 2

    async def test_get_many_when_filtered_returns_matching_users(self, user_repository):
        # Arrange
        created = await user_repository.create(
            CreateUserSchema(username="eve", email="eve@example.com")
        )
        await user_repository.create(
            CreateUserSchema(username="frank", email="frank@example.com")
        )

        # Act
        users = await user_repository.get_many(
            [ModelFields(field=User.id, value=created.id)]
        )

        # Assert
        assert len(users) == 1
        assert users[0].username == "eve"

    async def test_exists_when_user_exists_returns_true(self, user_repository):
        # Arrange
        created_user = await user_repository.create(
            CreateUserSchema(username="grace", email="grace@example.com")
        )

        # Act
        result = await user_repository.exists(
            [ModelFields(field=User.id, value=created_user.id)]
        )

        # Assert
        assert result is True

    async def test_exists_when_user_does_not_exist_returns_false(self, user_repository):
        # Arrange
        nonexistent_id = uuid.uuid4()

        # Act
        result = await user_repository.exists(
            [ModelFields(field=User.id, value=nonexistent_id)]
        )

        # Assert
        assert result is False

    async def test_update_one_when_valid_fields_updates_username(self, user_repository):
        # Arrange
        created_user = await user_repository.create(
            CreateUserSchema(username="henry", email="henry@example.com")
        )

        # Act
        updated = await user_repository.update_one(
            created_user, [ModelFields(field=User.username, value="henry_v2")]
        )

        # Assert
        assert updated.username == "henry_v2"

    async def test_delete_one_removes_user_from_db(self, user_repository):
        # Arrange
        created_user = await user_repository.create(
            CreateUserSchema(username="ida", email="ida@example.com")
        )

        # Act
        await user_repository.delete_one(created_user)

        # Assert
        exists = await user_repository.exists(
            [ModelFields(field=User.id, value=created_user.id)]
        )
        assert exists is False

    async def test_delete_many_removes_matching_users(self, user_repository):
        # Arrange
        created_user = await user_repository.create(
            CreateUserSchema(username="jack", email="jack@example.com")
        )
        await user_repository.create(
            CreateUserSchema(username="kate", email="kate@example.com")
        )

        # Act
        count = await user_repository.delete_many(
            [ModelFields(field=User.id, value=created_user.id)]
        )

        # Assert
        assert count == 1
        exists = await user_repository.exists(
            [ModelFields(field=User.id, value=created_user.id)]
        )
        assert exists is False
