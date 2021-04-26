from django import forms
from django.forms import Form,widgets,fields
from TestCase import models
from django.core.exceptions import ValidationError


class CaseForm(Form):
    case_id = fields.CharField(
            # max_length=32,
            label="Case_Id",
            widget=widgets.TextInput(attrs={'class': 'form-control'})
        )

    case_name = fields.CharField(
            # max_length=32,
            label="Case_Name",
            widget=widgets.TextInput(attrs={'class': 'form-control'})
        )

    function_id = fields.IntegerField(
            # max_length=32,
            label="Function",
            widget=widgets.Select(choices=models.Function.objects.values_list('id', 'function_name'),
                                  attrs={'class': 'form-control'})
        )

    sheet_id = fields.IntegerField(
            # max_length=32,
            label="Sheet",
            widget=widgets.Select(choices=models.Sheet.objects.values_list('id', 'sheet_name'),
                                  attrs={'class': 'form-control'})
        )

    attend_time = fields.CharField(
        # max_length=32,
        label="Attend_Time",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    procedure = fields.CharField(
        # max_length=32,
        label="Procedure",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
        )

    pass_criteria = fields.CharField(
        # max_length=32,
        label="Pass_Criteria",
        widget=widgets.Textarea(attrs={'class': 'form-control','style': 'height: 200px;width:500px'}),
        required=False
        )

    case_status = fields.ChoiceField(
        label="Case_Status",
        required=False,
        choices=((1, "open"), (2, "closed")),
        initial=1,
        widget=widgets.Select(attrs={'class': 'form-control'}),
    )

    case_note = fields.CharField(
        label="Case_Note",
        widget=widgets.Textarea(attrs={'class': 'form-control', }),
        required=False
    )

    test_plan_pic_path = fields.CharField(
        label="Attachment",
        widget=widgets.FileInput(),
        required=False
    )

    def clean(self):
        case = list(models.TestCase.objects.all().values_list('case_id'))
        case_id = self.cleaned_data.get("case_id")

        for i in case:
            if case_id in i:
                self.add_error("case_id", ValidationError("case_id已存在,请重新输入"))


class Case_updateForm(Form):
    case_id = fields.CharField(
            # max_length=32,
            label="Case_Id",
            widget=widgets.TextInput(attrs={'class': 'form-control','readonly': 'True'})
        )

    case_name = fields.CharField(
            # max_length=32,
            label="Case_Name",
            widget=widgets.TextInput(attrs={'class': 'form-control'})
        )

    function_id = fields.IntegerField(
            # max_length=32,
            label="Function",
            widget=widgets.Select(choices=models.Function.objects.values_list('id', 'function_name'),
                                  attrs={'class': 'form-control'})
        )

    sheet_id = fields.IntegerField(
            # max_length=32,
            label="Sheet",
            widget=widgets.Select(choices=models.Sheet.objects.values_list('id', 'sheet_name'),
                                  attrs={'class': 'form-control'})
        )

    attend_time = fields.CharField(
        # max_length=32,
        label="Attend_Time",
        widget=widgets.TextInput(attrs={'class': 'form-control', 'style': 'height: 40px;width:500px'}),
        required=False
    )

    procedure = fields.CharField(
        # max_length=32,
        label="Procedure",
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        required=False
        )

    pass_criteria = fields.CharField(
        # max_length=32,
        label="Pass_Criteria",
        widget=widgets.Textarea(attrs={'class': 'form-control','style': 'height: 200px;width:500px'}),
        required=False
        )

    case_status = fields.ChoiceField(
        label="Case_Status",
        required=False,
        choices=((1, "open"), (2, "closed")),
        initial=1,
        widget=widgets.Select(attrs={'class': 'form-control'}),
    )

    case_note = fields.CharField(
        label="Case_Note",
        widget=widgets.Textarea(attrs={'class': 'form-control', }),
        required=False
    )

    test_plan_pic_path = fields.CharField(
        label="Attachment",
        widget=widgets.FileInput(),
        required=False
    )
