from __future__ import annotations

import sys
from functools import partial
from typing import cast

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover

from rich.console import RenderableType
from rich.text import Text, TextType

from .. import events
from ..css._error_tools import friendly_list
from ..message import Message
from ..reactive import Reactive
from ..widget import Widget

ButtonVariant = Literal["default", "primary", "success", "warning", "error"]
_VALID_BUTTON_VARIANTS = {"default", "primary", "success", "warning", "error"}


class InvalidButtonVariant(Exception):
    pass


class Button(Widget, can_focus=True):
    """A simple clickable button."""

    DEFAULT_CSS = """
    Button {
        width: auto;
        min-width: 16;
        width: auto;
        height: 3;
        background: $panel;
        color: $text-panel;        
        border: none;
        border-top: tall $panel-lighten-2;
        border-bottom: tall $panel-darken-3;
        content-align: center middle;        
        text-style: bold;      
    }

    Button:focus {
        text-style: bold reverse;        
    }

    Button:hover {
        border-top: tall $panel-lighten-1;
        background: $panel-darken-2;
        color: $text-panel-darken-2;       
    }

    Button.-active {
        background: $panel;
        border-bottom: tall $panel-lighten-2;
        border-top: tall $panel-darken-2;                
        tint: $background 30%;
    }

    /* Primary variant */
    Button.-primary {
        background: $primary;
        color: $text-primary;
        border-top: tall $primary-lighten-3;
        border-bottom: tall $primary-darken-3;
      
    }

    Button.-primary:hover {
        background: $primary-darken-2;
        color: $text-primary-darken-2;

    }

    Button.-primary.-active {
        background: $primary;
        border-bottom: tall $primary-lighten-3;
        border-top: tall $primary-darken-3;
    
    }


    /* Success variant */
    Button.-success {
        background: $success;
        color: $text-success;
        border-top: tall $success-lighten-2;
        border-bottom: tall $success-darken-3;
      
    }

    Button.-success:hover {
        background: $success-darken-2;
        color: $text-success-darken-2;

    }

    Button.-success.-active {
        background: $success;
        border-bottom: tall $success-lighten-2;
        border-top: tall $success-darken-2;
    }

   
    /* Warning variant */
    Button.-warning {
        background: $warning;
        color: $text-warning;       
        border-top: tall $warning-lighten-2;
        border-bottom: tall $warning-darken-3;
    }

    Button.-warning:hover {
        background: $warning-darken-2;
        color: $text-warning-darken-1;
       
    }

    Button.-warning.-active {
        background: $warning;
        border-bottom: tall $warning-lighten-2;
        border-top: tall $warning-darken-2;
    }
   

    /* Error variant */
    Button.-error {
        background: $error;
        color: $text-error;
        border-top: tall $error-lighten-2;
        border-bottom: tall $error-darken-3;
     
    }

    Button.-error:hover {
        background: $error-darken-1;
        color: $text-error-darken-2;

    }

    Button.-error.-active {
        background: $error;
        border-bottom: tall $error-lighten-2;
        border-top: tall $error-darken-2;
    }

    """

    ACTIVE_EFFECT_DURATION = 0.3
    """When buttons are clicked they get the `-active` class for this duration (in seconds)"""

    class Pressed(Message, bubble=True):
        @property
        def button(self) -> Button:
            return cast(Button, self.sender)

    def __init__(
        self,
        label: TextType | None = None,
        disabled: bool = False,
        variant: ButtonVariant = "default",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Create a Button widget.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            variant (ButtonVariant): The variant of the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
        """
        super().__init__(name=name, id=id, classes=classes)

        if label is None:
            label = self.css_identifier_styled

        self.label: Text = label

        self.disabled = disabled
        if disabled:
            self.add_class("-disabled")

        if variant in _VALID_BUTTON_VARIANTS:
            if variant != "default":
                self.add_class(f"-{variant}")

        else:
            raise InvalidButtonVariant(
                f"Valid button variants are {friendly_list(_VALID_BUTTON_VARIANTS)}"
            )

    label: Reactive[RenderableType] = Reactive("")

    def validate_label(self, label: RenderableType) -> RenderableType:
        """Parse markup for self.label"""
        if isinstance(label, str):
            return Text.from_markup(label)
        return label

    def render(self) -> RenderableType:
        label = self.label.copy()
        label = Text.assemble(" ", label, " ")
        label.stylize(self.text_style)
        return label

    async def _on_click(self, event: events.Click) -> None:
        event.stop()
        self.press()

    def press(self) -> None:
        """Respond to a button press."""
        if self.disabled or not self.display:
            return
        # Manage the "active" effect:
        self._start_active_affect()
        # ...and let other components know that we've just been clicked:
        self.emit_no_wait(Button.Pressed(self))

    def _start_active_affect(self) -> None:
        """Start a small animation to show the button was clicked."""
        self.add_class("-active")
        self.set_timer(
            self.ACTIVE_EFFECT_DURATION, partial(self.remove_class, "-active")
        )

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter" and not self.disabled:
            self._start_active_affect()
            await self.emit(Button.Pressed(self))

    @classmethod
    def success(
        cls,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> Button:
        """Utility constructor for creating a success Button variant.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.

        Returns:
            Button: A Button widget of the 'success' variant.
        """
        return Button(
            label=label,
            disabled=disabled,
            variant="success",
            name=name,
            id=id,
            classes=classes,
        )

    @classmethod
    def warning(
        cls,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> Button:
        """Utility constructor for creating a warning Button variant.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.

        Returns:
            Button: A Button widget of the 'warning' variant.
        """
        return Button(
            label=label,
            disabled=disabled,
            variant="warning",
            name=name,
            id=id,
            classes=classes,
        )

    @classmethod
    def error(
        cls,
        label: TextType | None = None,
        disabled: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> Button:
        """Utility constructor for creating an error Button variant.

        Args:
            label (str): The text that appears within the button.
            disabled (bool): Whether the button is disabled or not.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.

        Returns:
            Button: A Button widget of the 'error' variant.
        """
        return Button(
            label=label,
            disabled=disabled,
            variant="error",
            name=name,
            id=id,
            classes=classes,
        )
