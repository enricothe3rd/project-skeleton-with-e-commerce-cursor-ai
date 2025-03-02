import re


class EvaluateValues:
    def __init__(self, data):
        self.data = data

    def _execute(self, pattern):
        regex = re.compile(pattern, re.I)

        if self.data == "" or self.data is None:
            return True
        else:
            match = regex.match(str(self.data))

            return bool(match)

    def alphanumeric(self):
        pattern = '^[A-Za-z0-9 ,.\']*$'
        return self._execute(pattern)

    def string_whitespace(self):
        pattern = '^[A-Za-z]([A-Za-z ]*)$'
        return self._execute(pattern)

    def string_no_whitespace(self):
        pattern = '^[A-Za-z]([A-Za-z]*)$'
        return self._execute(pattern)

    def integer(self):
        pattern = '^\d(\d*)?$'
        return self._execute(pattern)

    def float(self):
        pattern = '^\d(\d*)([.])(\d*)$'
        return self._execute(pattern)

    def email(self):
        pattern = '(.*)[@]([a-zA-z]*)?.com&'
        return self._execute(pattern)

    def mobile_num(self):
        pattern = '(^09|^639)([0-9]{9})$'
        return self._execute(pattern)

    def tin(self):
        pattern = '^([0-9]{3}-[0-9]{3}-[0-9]{3}-)(0{3}|0{4})$'
        return self._execute(pattern)

    def check_truth(self):
        result = True

        for value in self.data:
            if value is False:
                result = False

        return result


class ValidateEmployeeOnboarding:
    def __init__(self, data):
        self.data = data

    def execute(self):
        data = self.data
        truth = True

        validate = [
            self._validate_details(data['details']),
            self._validate_addresses(data['addresses']),
            self._validate_contract(data['contract']),
            self._validate_bank(data['bank_details']),
            self._validate_leaves(data['leaves']),
            self._validate_allowances(data['allowances']),
            self._validate_schedules(data['schedules']),
            self._validate_deductions(data['deductions'])
        ]

        for result in validate:
            truth = EvaluateValues(result).check_truth()

        return truth

    @staticmethod
    def _validate_details(data):
        validate = EvaluateValues

        results = [
            validate(data['badge_no']).integer(),
            validate(data['first_name']).string_whitespace(),
            validate(data['middle_name']).string_whitespace(),
            validate(data['last_name']).string_whitespace(),
            validate(data['suffix']).string_no_whitespace(),
            validate(data['professional_extensions']).string_no_whitespace(),
            validate(data['email']).email(),
            validate(data['mobile']).mobile_num(),
            validate(data['tin']).tin(),
        ]

        return results

    @staticmethod
    def _validate_contract(data):
        validate = EvaluateValues

        results = [
            validate(data['name']).alphanumeric(),
            validate(data['hourly_rate']).float(),
            validate(data['daily_work_hours']).float()
        ]

        return results

    @staticmethod
    def _validate_addresses(data):
        validate = EvaluateValues
        results = []

        for value in data:
            results.append(validate(value['line']).alphanumeric())
            results.append(validate(value['barangay']).alphanumeric())
            results.append(validate(value['city']).alphanumeric())
            results.append(validate(value['province']).alphanumeric())
            results.append(validate(value['zip']).integer())
        return results

    @staticmethod
    def _validate_bank(data):
        validate = EvaluateValues
        results = []

        for value in data:
            results.append(validate(value['bank_name']).alphanumeric())
            results.append(validate(value['bank_no']).integer())
        return results

    @staticmethod
    def _validate_leaves(data):
        validate = EvaluateValues
        results = []

        for value in data:
            results.append(
                validate(value['credits']).alphanumeric()
            )
        return results

    @staticmethod
    def _validate_allowances(data):
        validate = EvaluateValues
        results = []

        for value in data:
            results.append(validate(value['name']).alphanumeric())
            results.append(validate(value['amount']).float())
        return results

    @staticmethod
    def _validate_schedules(data):
        validate = EvaluateValues
        results = [validate(data['headers']['name']).string_whitespace()]

        print(data["lines"])
        for lines in data['lines']:
            results.append(validate(lines['duration']).float())

        return results

    @staticmethod
    def _validate_deductions(data):
        validate = EvaluateValues
        results = []

        for value in data:
            results.append(
                validate(value['deduction_id']).integer()
            )

        return results


def validate_number(value, value_type="int", field_name="value"):
    """
    Validates that the given value is a number (int or float) and is not negative.

    :param value: The value to validate.
    :param value_type: "int" for integer validation, "float" for floating-point validation.
    :param field_name: The name of the field (for error messages).
    :return: The converted number if valid, otherwise raises ValueError.
    """
    try:
        if value_type == "int":
            value = int(value)  # Convert to integer
        elif value_type == "float":
            value = float(value)  # Convert to float
        else:
            raise ValueError("Invalid value_type. Use 'int' or 'float'.")

        if value < 0:
            raise ValueError(f"{field_name.capitalize()} cannot be negative.")

        return value
    except ValueError:
        raise ValueError(f"{field_name.capitalize()} must be a valid {value_type} and cannot be negative.")


def validate_string(value, field_name):
    """
    Validates that the provided value is a string.

    Args:
        value: The value to validate.
        field_name: The name of the field being validated (for error messaging).

    Returns:
        The validated string value if valid.

    Raises:
        ValueError: If the value is not a string.
    """
    if not isinstance(value, str):
        raise ValueError(f"Invalid value for {field_name}. Expected a string, but got {type(value).__name__}.")
    return value