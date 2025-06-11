from django import forms

class CartAddProductForm(forms.Form):
    """Form for adding products to cart"""
    quantity = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 21)],
        coerce=int,
        initial=1,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )