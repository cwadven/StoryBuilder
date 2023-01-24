from django.forms import inlineformset_factory
from django.test import TestCase

from account.models import User
from hint.admin_forms import SheetHintInlineFormset
from hint.models import SheetHint
from story.admin_forms import SheetAdminForm
from story.models import Story, Sheet


class TestStoryAdminForm(TestCase):
    def setUp(self):
        self.super_user = User.objects.create_superuser(
            username='superuser', password='secret', email='admin@example.com'
        )
        self.client.login(username='superuser', password='secret')
        self.story = Story.objects.create(
            author=self.super_user,
            title='test_story',
            description='test_description',
        )
        self.start_sheet = Sheet.objects.create(
            story=self.story,
            title='test_title',
            question='test_question',
            image='https://image.test',
            background_image='https://image.test',
            is_start=True,
            is_final=False,
        )
        self.SheetHintInlineFormSet = inlineformset_factory(
            Sheet, SheetHint, form=SheetAdminForm, formset=SheetHintInlineFormset
        )
        self.data = {
            'sheethint_set-INITIAL_FORMS': 0,
            'sheethint_set-MAX_NUM_FORMS': 1000,
            'sheethint_set-TOTAL_FORMS': 1,
            'sheethint_set-0-hint': '힌트0번',
            'sheethint_set-0-sequence': 1,
            'sheethint_set-0-is_deleted': False,
            'sheethint_set-0-point': 10,
        }

    def test_sheet_hint_formset_is_valid(self):
        # Given:
        # When:
        formset = self.SheetHintInlineFormSet(self.data, instance=self.start_sheet)
        # Then:
        self.assertTrue(formset.is_valid())

    def test_sheet_hint_formset_should_raise_error_when_sequence_has_same_value(self):
        # Given: 동일한 sequence 적용
        self.data['sheethint_set-TOTAL_FORMS'] = 2
        self.data['sheethint_set-1-hint'] = '힌트1번'
        self.data['sheethint_set-1-sequence'] = 1
        self.data['sheethint_set-1-is_deleted'] = False
        self.data['sheethint_set-1-point'] = 10

        # When:
        formset = self.SheetHintInlineFormSet(self.data, instance=self.start_sheet)

        # Then: 에러 반환
        self.assertFalse(formset.is_valid())
        self.assertEqual(formset.non_form_errors()[0], '동일한 sequence 를 가진 Sheet Hint 가 있습니다.')

    def test_sheet_hint_formset_should_not_raise_error_when_sequence_has_same_value_but_is_deleted(self):
        # Given: 동일한 sequence 적용 하지만 is_deleted 는 True
        self.data['sheethint_set-TOTAL_FORMS'] = 2
        self.data['sheethint_set-1-hint'] = '힌트1번'
        self.data['sheethint_set-1-sequence'] = 1
        self.data['sheethint_set-1-is_deleted'] = True
        self.data['sheethint_set-1-point'] = 10

        # When:
        formset = self.SheetHintInlineFormSet(self.data, instance=self.start_sheet)

        # Then:
        self.assertTrue(formset.is_valid())
