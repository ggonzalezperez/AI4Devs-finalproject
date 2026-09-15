from datetime import date

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ChildCreate(BaseModel):
    name: str
    birthdate: date
    # RF-ONB-03: exactamente 4 dígitos. La regla se aplica en servidor, no solo
    # en el formulario: la validación de cliente es cortesía, no una barrera.
    pin: str = Field(pattern=r"^\d{4}$")
    avatar: str = "fox"


class ChildPinLogin(BaseModel):
    pin: str


class ChildRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    birthdate: date
    avatar: str
    avatar_image_url: str | None = None

    @computed_field
    @property
    def age(self) -> int:
        today = date.today()
        return (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )


class AvatarGenerate(BaseModel):
    description: str = Field(min_length=2, max_length=120)
