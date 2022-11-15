""" Test of log in view """


class LogInViewTestCase(TestCase,LogInTester):

    fixtures = ['microblogs/tests/fixtures/default_user']

    def setUp(self):
        self.url = reverse('log_in')

        self.user = User.objects.create_user('@johndoe',
            first_name = 'John',
            last_name = 'Doe',
            email = 'johndoe@example.org',
            bio = 'Hey, this is crazy!',
            password = 'Password123',
            is_active = True

        )

    def test_sign_up_url(self):
        self.assertEqual(self.url, '/log_in/')
