from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from uuid import uuid4

from starfish.router.models import Site, Project


class DatabaseConnectionTest(TestCase):
    """Test that database is connected and migrations are applied"""

    def test_database_connection(self):
        """Verify database connectivity"""
        from django.db import connection
        cursor = connection.cursor()
        self.assertIsNotNone(cursor)

    def test_migrations_applied(self):
        """Ensure all migrations have been applied"""
        from django.db.migrations.executor import MigrationExecutor
        from django.db import connection
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        self.assertEqual(len(plan), 0, "Unapplied migrations found")


class SiteModelTest(TestCase):
    """Test core Site functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_site_creation(self):
        """Test creating a site with required fields"""
        site = Site.objects.create(
            name='Test Site',
            description='A test site',
            uid=uuid4(),
            owner=self.user
        )
        self.assertEqual(site.name, 'Test Site')
        self.assertEqual(site.status, Site.SiteStatus.CONNECTED)
        self.assertIsNotNone(site.created_at)


class ProjectModelTest(TestCase):
    """Test core Project functionality"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.site = Site.objects.create(
            name='Test Site',
            description='A test site',
            uid=uuid4(),
            owner=self.user
        )

    def test_project_creation(self):
        """Test creating a project"""
        project = Project.objects.create(
            name='Test Project',
            description='A test project',
            site=self.site,
            batch=0
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.batch, 0)
        self.assertIsNotNone(project.created_at)
