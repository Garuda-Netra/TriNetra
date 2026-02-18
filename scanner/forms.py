from django import forms

# Shared CSS class from trinetra-fx.css
_INPUT_CLASS = "tri-input"


class ScanForm(forms.Form):
    target = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": _INPUT_CLASS,
                "placeholder": "e.g. 127.0.0.1 or scanme.nmap.org",
            }
        ),
    )
    ports = forms.CharField(
        max_length=255,
        help_text="Use range (1-1024) or list (22,80,443)",
        widget=forms.TextInput(
            attrs={
                "class": _INPUT_CLASS,
                "placeholder": "e.g. 20-100 or 22,80,443",
            }
        ),
    )
    timeout = forms.FloatField(
        initial=0.5,
        min_value=0.05,
        max_value=5.0,
        widget=forms.NumberInput(
            attrs={
                "class": _INPUT_CLASS,
                "step": "0.05",
            }
        ),
    )


class HistoryFilterForm(forms.Form):
    target = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": _INPUT_CLASS,
                "placeholder": "Filter by target",
                "id": "id_target_filter",
            }
        ),
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": _INPUT_CLASS,
                "id": "id_start_date_filter",
            }
        ),
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": _INPUT_CLASS,
                "id": "id_end_date_filter",
            }
        ),
    )
