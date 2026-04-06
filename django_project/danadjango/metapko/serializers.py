from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from .models import (
    Building,
    CalendarEvent,
    ClassSession,
    ContactEntry,
    Course,
    CustomerOrder,
    Department,
    FaqEntry,
    IikoOutlet,
    MenuItem,
    NewsPost,
    OrderLine,
    Room,
    ServiceTicket,
    StudyGroup,
    StudyProgram,
    Teacher,
)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'is_active', 'sort_order']


class StudyProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyProgram
        fields = ['id', 'name', 'code', 'level', 'is_active', 'sort_order']


class StudyGroupSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True, allow_null=True)

    class Meta:
        model = StudyGroup
        fields = [
            'id',
            'name',
            'program',
            'program_name',
            'program_code',
            'intake_year',
            'is_active',
            'sort_order',
        ]


class StudyGroupBriefSerializer(serializers.ModelSerializer):
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = StudyGroup
        fields = ['id', 'name', 'program', 'program_name', 'intake_year']


class TeacherSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)

    class Meta:
        model = Teacher
        fields = [
            'id',
            'full_name',
            'department',
            'department_name',
            'position',
            'email',
            'phone',
            'is_active',
        ]


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True, allow_null=True)
    study_groups = StudyGroupBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'code',
            'description',
            'teacher',
            'teacher_name',
            'study_groups',
            'is_active',
        ]


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'code', 'address', 'is_active', 'sort_order']


class RoomSerializer(serializers.ModelSerializer):
    building_name = serializers.CharField(source='building.name', read_only=True)
    building_code = serializers.CharField(source='building.code', read_only=True, allow_null=True)

    class Meta:
        model = Room
        fields = [
            'id',
            'building',
            'building_name',
            'building_code',
            'name',
            'floor',
            'capacity',
            'is_active',
            'sort_order',
        ]


class RoomBriefSerializer(serializers.ModelSerializer):
    building_code = serializers.CharField(source='building.code', read_only=True, allow_null=True)
    building_name = serializers.CharField(source='building.name', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'name', 'floor', 'building', 'building_code', 'building_name']


class ClassSessionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True, allow_null=True)
    room_detail = RoomBriefSerializer(source='room_ref', read_only=True, allow_null=True)
    room_display = serializers.SerializerMethodField()

    class Meta:
        model = ClassSession
        fields = [
            'id',
            'course',
            'course_title',
            'title',
            'teacher',
            'teacher_name',
            'starts_at',
            'ends_at',
            'room_ref',
            'room_detail',
            'room',
            'room_display',
            'notes',
        ]

    def get_room_display(self, obj):
        if obj.room_ref_id:
            b = obj.room_ref.building
            prefix = (b.code or b.name or '').strip()
            return f'{prefix}, {obj.room_ref.name}'.strip(', ')
        return (obj.room or '').strip()


class FaqEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqEntry
        fields = ['id', 'question', 'answer', 'keywords', 'sort_order', 'is_active']


class CalendarEventSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)

    class Meta:
        model = CalendarEvent
        fields = [
            'id',
            'title',
            'kind',
            'kind_display',
            'starts_on',
            'ends_on',
            'description',
            'is_published',
            'sort_order',
        ]


class NewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = [
            'id',
            'title',
            'slug',
            'summary',
            'body',
            'published_at',
            'is_published',
            'is_pinned',
            'sort_order',
        ]


class ContactEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactEntry
        fields = [
            'id',
            'title',
            'role_hint',
            'phone',
            'email',
            'address',
            'office_hours',
            'notes',
            'is_active',
            'sort_order',
        ]


class IikoOutletSerializer(serializers.ModelSerializer):
    class Meta:
        model = IikoOutlet
        fields = ['id', 'name', 'address', 'phone', 'is_active']


class MenuItemSerializer(serializers.ModelSerializer):
    outlet_name = serializers.CharField(source='outlet.name', read_only=True, allow_null=True)

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'outlet',
            'outlet_name',
            'name',
            'category',
            'price',
            'is_available',
            'sort_order',
        ]


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = ['id', 'menu_item', 'dish_name', 'quantity', 'unit_price']


class CustomerOrderSerializer(serializers.ModelSerializer):
    lines = OrderLineSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerOrder
        fields = [
            'id',
            'outlet',
            'status',
            'customer_name',
            'phone',
            'notes',
            'external_ref',
            'created_at',
            'updated_at',
            'lines',
        ]


class OrderLineWriteSerializer(serializers.Serializer):
    menu_item = serializers.PrimaryKeyRelatedField(
        queryset=MenuItem.objects.filter(is_available=True),
        required=False,
        allow_null=True,
    )
    dish_name = serializers.CharField(required=False, allow_blank=True, max_length=255)
    quantity = serializers.IntegerField(min_value=1, default=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, min_value=Decimal('0'))

    def validate(self, data):
        if not data.get('menu_item') and not (data.get('dish_name') or '').strip():
            raise serializers.ValidationError('Укажите menu_item или dish_name.')
        return data


class CustomerOrderCreateSerializer(serializers.ModelSerializer):
    lines = OrderLineWriteSerializer(many=True)

    class Meta:
        model = CustomerOrder
        fields = ['outlet', 'customer_name', 'phone', 'notes', 'external_ref', 'lines']

    def validate_lines(self, value):
        if not value:
            raise serializers.ValidationError('Нужна минимум одна строка заказа.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        order = CustomerOrder.objects.create(**validated_data)
        for raw in lines_data:
            menu_item = raw.get('menu_item')
            qty = raw.get('quantity', 1)
            dish_name = (raw.get('dish_name') or '').strip()
            if menu_item:
                if not dish_name:
                    dish_name = menu_item.name
                unit_price = raw.get('unit_price')
                if unit_price is None:
                    unit_price = menu_item.price
            else:
                unit_price = raw.get('unit_price')
                if unit_price is None:
                    raise serializers.ValidationError({'lines': 'Без menu_item нужна unit_price.'})
            OrderLine.objects.create(
                order=order,
                menu_item=menu_item,
                dish_name=dish_name,
                quantity=qty,
                unit_price=unit_price,
            )
        return order


class ServiceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTicket
        fields = [
            'id',
            'title',
            'description',
            'outlet',
            'status',
            'priority',
            'requester_name',
            'contact',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
