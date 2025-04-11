from rest_framework import serializers


class ActivationCodeSerializer(serializers.Serializer):
    """
       This serializer is used to validate the activation code provided by the user during the account activation process.

        **Fields**:
        - **activation_code** (str): A string field that accepts a maximum of 8 characters.
          This code is expected to be sent to the user and then provided back for validation.
    """
    activation_code = serializers.CharField(max_length=8)
