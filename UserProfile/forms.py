from django.forms import Form,widgets,fields
from UserProfile import models
from django.core.exceptions import ValidationError


class UserForm(Form):
    username = fields.CharField(
        # max_length=16,
        label="工号",
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'maxlength': '32'}),
        error_messages={
            "required": "用户名不能为空"}
    )

    name = fields.CharField(
        # max_length=16,
        label="姓名",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            "required": "姓名不能为空"}
    )

    job_name = fields.CharField(
        # max_length=16,
        label="英文名",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            "required": "英文名不能为空"}
    )

    gender = fields.ChoiceField(
        # max_length=4,
        label="性别",
        required=False,
        choices=((1, "男"), (2, "女"), (3, "保密")),
        initial=3,
        widget=widgets.Select(attrs={'class': 'form-control'}),
    )

    belone_to_team_id = fields.IntegerField(
        # max_length=16,
        label="组别",
        widget=widgets.Select(choices=models.Team.objects.values_list('id', 'name'),
                              attrs={'class': 'form-control'}),
        required=False
    )

    join_in_time = fields.DateField(
        # max_length=32,
        label="入职时间",
        widget=widgets.DateInput(
            attrs={'class': 'form-control',
                   'autocomplete': 'off',
                   'value': '2018-01-01',
                   'readonly': 'true'}),
        required=False
    )

    shot_number = fields.CharField(
        # max_length=8,
        label="手机短号",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    phone_number = fields.CharField(
        # max_length=11,
        label="手机号",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    university = fields.CharField(
        # max_length=128,
        label="毕业学校",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    major = fields.CharField(
        # max_length=128,
        label="专业",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    role_id = fields.IntegerField(
        # max_length=16,
        label="权限",
        widget=widgets.Select(choices=models.Role.objects.values_list('id', 'name'),
            attrs={'class': 'form-control'}),
        required=False
    )

    # leave_time = fields.DateTimeField(
    #     # max_length=32,
    #     label="离职时间",
    #     widget=widgets.DateTimeInput(attrs={'class': 'form-control','autocomplete':'off','disabled':'True'}),
    #     required=False
    # )

    password = fields.CharField(
        # max_length=32,
        label="密码",
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            "required": "密码不能为空"}
    )

    re_password = fields.CharField(
        # max_length=32,
        label="确认密码",
        widget=widgets.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={
            "required": "重复密码不能为空"}
    )

    # 确认两次密码一致
    def clean(self):
        user = list(models.UserInfo.objects.all().values_list('username'))
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        re_password = self.cleaned_data.get("re_password")

        for i in user:
            if username in i:
                # raise forms.ValidationError('用户名已存在,请重新尝试登录')
                self.add_error("username", ValidationError("用户名已存在,请重新输入"))

        if re_password and re_password != password:
            self.add_error("re_password", ValidationError("两次密码不一致"))

        else:
            return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields["belone_to_team_id"].widget.choices = models.Team.objects.values_list("id", "name")


class UpdateUserForm(Form):
    username = fields.CharField(
        # max_length=16,
        label="工号",

        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'readonly': 'True'}),
        error_messages={
            "required": "用户名不能为空"}
    )

    name = fields.CharField(
        # max_length=16,
        label="姓名",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            "required": "姓名不能为空"}
    )

    job_name = fields.CharField(
        # max_length=16,
        label="英文名",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        error_messages={
            "required": "英文名不能为空"}
    )

    gender = fields.ChoiceField(
        # max_length=4,
        label="性别",
        required=False,
        choices=((1, "男"), (2, "女"), (3, "保密")),
        initial=3,
        widget=widgets.Select(attrs={'class': 'form-control'}),
    )

    join_in_time = fields.DateField(
        # max_length=32,
        label="入职时间",
        widget=widgets.DateInput(attrs={'class': 'form-control',
                                        'value': '2018-01-01',
                                        'readonly': 'true'}),
        required=False
    )

    shot_number = fields.CharField(
        # max_length=8,
        label="手机短号",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    phone_number = fields.CharField(
        # max_length=11,
        label="手机号",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    belone_to_team_id = fields.IntegerField(
        # max_length=16,
        label="组别",
        widget=widgets.Select(attrs={'class': 'form-control'}),
        required=False
    )

    university = fields.CharField(
        # max_length=128,
        label="毕业学校",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    major = fields.CharField(
        # max_length=128,
        label="专业",
        widget=widgets.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    role_id = fields.IntegerField(
        # max_length=16,
        label="权限",
        widget=widgets.Select(choices=models.Role.objects.values_list('id', 'name'),
                              attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)
        self.fields["belone_to_team_id"].widget.choices = models.Team.objects.values_list("id", "name")


