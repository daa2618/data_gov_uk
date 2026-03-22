from data_gov_uk.exceptions import OrganizationNotFound, PackageNotFound


class TestOrganizationNotFound:
    def test_is_exception_subclass(self):
        assert issubclass(OrganizationNotFound, Exception)

    def test_message(self):
        exc = OrganizationNotFound("org missing")
        assert str(exc) == "org missing"


class TestPackageNotFound:
    def test_is_exception_subclass(self):
        assert issubclass(PackageNotFound, Exception)

    def test_message(self):
        exc = PackageNotFound("pkg missing")
        assert str(exc) == "pkg missing"
