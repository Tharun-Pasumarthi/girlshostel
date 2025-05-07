from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import User, StudentProfile, WardenProfile
from rooms.models import Room, RoomAllocation
from payments.models import FeeStructure, Payment
from attendance.models import Attendance, LeaveRequest
from mess.models import Menu, MealFeedback
from complaints.models import Complaint
from notifications.models import Notification, Announcement
from gallery.models import Event, GalleryCategory, GalleryImage

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')

        # Create admin user
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='ADMIN'
        )
        self.stdout.write('Created admin user')

        # Create warden users
        warden = User.objects.create_user(
            email='warden@example.com',
            password='warden123',
            first_name='Sarah',
            last_name='Johnson',
            role='WARDEN'
        )
        WardenProfile.objects.create(
            user=warden,
            designation='Senior Warden',
            department='Hostel Administration',
            joining_date=timezone.now().date() - timedelta(days=365)
        )
        self.stdout.write('Created warden user')

        # Create student users
        students = []
        for i in range(1, 21):
            student = User.objects.create_user(
                email=f'student{i}@example.com',
                password='student123',
                first_name=f'Student{i}',
                last_name=f'Last{i}',
                role='STUDENT'
            )
            StudentProfile.objects.create(
                user=student,
                roll_number=f'STU{i:03d}',
                course='Computer Science',
                semester=random.randint(1, 8),
                blood_group=random.choice(['A+', 'B+', 'O+', 'AB+']),
                parent_name=f'Parent{i}',
                parent_phone=f'9876543{i:03d}',
                parent_email=f'parent{i}@example.com'
            )
            students.append(student)
        self.stdout.write('Created student users')

        # Create rooms
        rooms = []
        for i in range(1, 11):
            room = Room.objects.create(
                room_number=f'10{i:02d}',
                room_type=random.choice(['SINGLE', 'DOUBLE', 'TRIPLE']),
                floor=1,
                capacity=random.randint(1, 3),
                is_available=True,
                description=f'Room {i} description',
                amenities={'wifi': True, 'ac': True, 'attached_bathroom': True}
            )
            rooms.append(room)
        self.stdout.write('Created rooms')

        # Allocate rooms to students
        for i, student in enumerate(students):
            room = rooms[i % len(rooms)]
            RoomAllocation.objects.create(
                room=room,
                student=student,
                allocated_by=warden,
                allocation_date=timezone.now().date() - timedelta(days=30),
                check_in_date=timezone.now().date() - timedelta(days=30),
                is_active=True
            )
        self.stdout.write('Allocated rooms to students')

        # Create fee structure
        fee_types = ['MONTHLY', 'SECURITY', 'MAINTENANCE']
        for fee_type in fee_types:
            FeeStructure.objects.create(
                fee_type=fee_type,
                amount=random.randint(1000, 5000),
                description=f'{fee_type} fee description',
                is_active=True
            )
        self.stdout.write('Created fee structure')

        # Create payments
        for student in students:
            for _ in range(3):
                Payment.objects.create(
                    student=student,
                    fee_structure=FeeStructure.objects.first(),
                    amount=random.randint(1000, 5000),
                    payment_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    due_date=timezone.now().date() + timedelta(days=random.randint(1, 30)),
                    status=random.choice(['PENDING', 'COMPLETED', 'FAILED']),
                    payment_method=random.choice(['ONLINE', 'CASH', 'CHEQUE']),
                    transaction_id=f'TXN{random.randint(1000, 9999)}',
                    receipt_number=f'RCPT{random.randint(1000, 9999)}'
                )
        self.stdout.write('Created payments')

        # Create attendance records
        for student in students:
            for i in range(30):
                Attendance.objects.create(
                    student=student,
                    date=timezone.now().date() - timedelta(days=i),
                    status=random.choice(['PRESENT', 'ABSENT', 'LATE']),
                    check_in_time=timezone.now().time(),
                    check_out_time=timezone.now().time(),
                    marked_by=warden
                )
        self.stdout.write('Created attendance records')

        # Create leave requests
        for student in students:
            LeaveRequest.objects.create(
                student=student,
                leave_type=random.choice(['SICK', 'EMERGENCY', 'PERSONAL']),
                start_date=timezone.now().date() + timedelta(days=random.randint(1, 10)),
                end_date=timezone.now().date() + timedelta(days=random.randint(11, 20)),
                reason='Sample leave reason',
                status=random.choice(['PENDING', 'APPROVED', 'REJECTED']),
                approved_by=warden if random.choice([True, False]) else None
            )
        self.stdout.write('Created leave requests')

        # Create mess menu
        for i in range(7):
            Menu.objects.create(
                date=timezone.now().date() + timedelta(days=i),
                meal_type=random.choice(['BREAKFAST', 'LUNCH', 'DINNER']),
                items={
                    'main_course': 'Sample main course',
                    'side_dish': 'Sample side dish',
                    'dessert': 'Sample dessert'
                },
                created_by=warden
            )
        self.stdout.write('Created mess menu')

        # Create complaints
        for student in students:
            Complaint.objects.create(
                student=student,
                category=random.choice(['MAINTENANCE', 'CLEANING', 'ELECTRICAL']),
                title=f'Complaint from {student.get_full_name()}',
                description='Sample complaint description',
                status=random.choice(['PENDING', 'IN_PROGRESS', 'RESOLVED']),
                priority=random.choice(['LOW', 'MEDIUM', 'HIGH']),
                assigned_to=warden if random.choice([True, False]) else None
            )
        self.stdout.write('Created complaints')

        # Create announcements
        for i in range(5):
            Announcement.objects.create(
                title=f'Announcement {i+1}',
                content=f'Sample announcement content {i+1}',
                type=random.choice(['GENERAL', 'EMERGENCY', 'MAINTENANCE']),
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=7),
                is_active=True,
                created_by=warden
            )
        self.stdout.write('Created announcements')

        # Create events
        for i in range(5):
            Event.objects.create(
                title=f'Event {i+1}',
                description=f'Sample event description {i+1}',
                start_date=timezone.now() + timedelta(days=i*7),
                end_date=timezone.now() + timedelta(days=i*7 + 1),
                location='Main Hall',
                organizer=warden,
                is_active=True
            )
        self.stdout.write('Created events')

        self.stdout.write(self.style.SUCCESS('Successfully populated database with sample data')) 