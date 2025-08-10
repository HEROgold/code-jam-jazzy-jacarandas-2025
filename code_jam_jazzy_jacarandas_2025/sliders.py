import reflex as rx

class PhoneNumberSlider(rx.State):
    area: int = 1
    phone_rest: list[int] = [0, 0, 0, 0]


    @rx.event
    def set_area(self, value: list[int | float]):
        self.area = value[0]
    

    @rx.event
    def phone(self, value: list[int | float], index: int):
        self.phone_rest[index] = value[0]


    @rx.var
    def as_str(self) -> str:
        number = ''.join(map(str, self.phone_rest))
        return f"+{self.area} {number}"
    
    @staticmethod
    def new(*, max_digits: tuple[int] = (3, 3, 3, 3), **kw):
        return rx.vstack(
            rx.heading(f"Enter phone number:"),
            rx.heading(PhoneNumberSlider.as_str),
            PhoneNumberSlider.make_area_code_slider(),
            *[PhoneNumberSlider.make_slider(idx, exp) for idx, exp in enumerate(max_digits)],
            **kw,
        )
    

    @staticmethod
    def make_area_code_slider():
        return rx.slider(
            min=1,
            max=998, # valid country range: 1..=998
            step=1,
            value=[PhoneNumberSlider.area],
            on_change=PhoneNumberSlider.set_area
        ),


    @staticmethod
    def make_slider(index, max_exp):
        """
        Creates a slider controlling PhoneState,
        `index` is the index of `PhoneState.rest` and max_exp just says how many digits
        this slider supports, for example max_exp=3 has range 0..=999
        this can be called like this in a vstack/hstack:
        ```
        rx.vstack(*[make_sliders(idx, exp) for idx, exp in enumerate(sliders)])
        ```
        """
        return rx.slider(
            min=0,
            max=10 ** max_exp - 1,
            step=1,
            value=[PhoneNumberSlider.phone_rest[index]],
            on_change=lambda value: PhoneNumberSlider.phone(value, index)
        )
