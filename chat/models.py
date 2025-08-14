from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.utils import timezone
import uuid
from user.models import CustomUser
import os

User = CustomUser


def sticker_upload_path(instance, filename):
    return f"stickers/{instance.pack.id}/{filename}"


def gif_upload_path(instance, filename):
    return f"gifs/{uuid.uuid4()}/{filename}"


class StickerPack(models.Model):
    """مدل پک استیکر با تمام ویژگی‌های پیشرفته"""

    PACK_TYPES = (
        ('ST', 'Static Sticker'),
        ('AN', 'Animated Sticker'),
        ('VI', 'Video Sticker'),
        ('EM', 'Emoji Pack'),
    )

    # اطلاعات اصلی
    title = models.CharField(max_length=100)
    identifier = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    creator = models.ForeignKey(User, related_name='created_sticker_packs', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # تنظیمات فنی
    pack_type = models.CharField(max_length=2, choices=PACK_TYPES, default='ST')
    is_animated = models.BooleanField(default=False)
    is_video = models.BooleanField(default=False)
    is_emoji = models.BooleanField(default=False)
    tgs_support = models.BooleanField(default=False)  # پشتیبانی از فرمت TGS برای استیکرهای متحرک تلگرام

    # تنظیمات انتشار
    is_official = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)  # پک مخصوص کاربران پریمیوم

    # آمار و ارقام
    usage_count = models.PositiveBigIntegerField(default=0)
    downloads = models.PositiveBigIntegerField(default=0)
    rating = models.FloatField(default=0.0)

    # اطلاعات ظاهری
    thumbnail = models.ImageField(upload_to='sticker_pack_thumbnails/', null=True, blank=True)
    cover_sticker = models.ForeignKey('Sticker', null=True, blank=True, on_delete=models.SET_NULL,
                                      related_name='cover_for_packs')

    # دسته‌بندی
    tags = models.ManyToManyField('StickerTag', related_name='sticker_packs', blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['identifier']),
            models.Index(fields=['is_public']),
            models.Index(fields=['creator']),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_pack_type_display()})"

    def update_usage_count(self):
        """به‌روزرسانی تعداد استفاده از پک"""
        self.usage_count = Sticker.objects.filter(pack=self).aggregate(
            total_usage=models.Sum('usage_count')
        )['total_usage'] or 0
        self.save()


class Sticker(models.Model):
    """مدل استیکر با قابلیت‌های پیشرفته"""

    STICKER_FORMATS = (
        ('WEBP', 'WebP'),
        ('PNG', 'PNG'),
        ('JPG', 'JPG'),
        ('TGS', 'Telegram Animated Sticker'),
        ('WEBM', 'WebM Video'),
    )

    pack = models.ForeignKey(StickerPack, related_name='stickers', on_delete=models.CASCADE)
    file = models.FileField(upload_to=sticker_upload_path)
    format = models.CharField(max_length=4, choices=STICKER_FORMATS, default='WEBP')
    emoji = models.CharField(max_length=10, blank=True)  # ایموجی مرتبط

    # ابعاد و ویژگی‌های فنی
    width = models.PositiveSmallIntegerField(default=512)
    height = models.PositiveSmallIntegerField(default=512)
    frame_rate = models.PositiveSmallIntegerField(null=True, blank=True)  # برای استیکرهای متحرک
    duration = models.FloatField(null=True, blank=True)  # مدت زمان پخش (ثانیه)
    file_size = models.PositiveIntegerField(default=0)  # حجم فایل به بایت

    # آمار استفاده
    usage_count = models.PositiveBigIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    # اطلاعات متا
    keywords = models.CharField(max_length=255, blank=True)  # کلمات کلیدی برای جستجو
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pack', 'id']
        indexes = [
            models.Index(fields=['emoji']),
            models.Index(fields=['usage_count']),
        ]

    def __str__(self):
        return f"Sticker {self.id} in {self.pack.title}"

    def save(self, *args, **kwargs):
        """محاسبه خودکار حجم فایل هنگام ذخیره"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def increment_usage(self):
        """افزایش شمارنده استفاده از استیکر"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save()
        self.pack.update_usage_count()


class StickerTag(models.Model):
    """دسته‌بندی برای پک‌های استیکر"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class GIF(models.Model):
    """مدل گیف با قابلیت‌های پیشرفته"""

    GIF_SOURCES = (
        ('UP', 'User Uploaded'),
        ('TG', 'Telegram GIFs'),
        ('GP', 'GIPHY'),
        ('TR', 'Tenor'),
    )

    # اطلاعات اصلی
    title = models.CharField(max_length=100, blank=True)
    identifier = models.CharField(max_length=50, blank=True)  # شناسه از منبع اصلی
    source = models.CharField(max_length=2, choices=GIF_SOURCES, default='UP')
    file = models.FileField(upload_to=gif_upload_path)
    thumbnail = models.ImageField(upload_to='gif_thumbnails/', null=True, blank=True)

    # ابعاد و ویژگی‌های فنی
    width = models.PositiveSmallIntegerField(default=480)
    height = models.PositiveSmallIntegerField(default=270)
    duration = models.FloatField(default=0.0)  # مدت زمان پخش (ثانیه)
    frame_rate = models.PositiveSmallIntegerField(default=30)
    file_size = models.PositiveIntegerField(default=0)  # حجم فایل به بایت

    # آمار استفاده
    usage_count = models.PositiveBigIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)

    # دسته‌بندی و تگ‌ها
    tags = models.ManyToManyField('GIFTag', related_name='gifs', blank=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)

    # اطلاعات منبع
    source_url = models.URLField(blank=True)
    attribution = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['usage_count']),
            models.Index(fields=['source']),
        ]

    def __str__(self):
        return f"GIF: {self.title or self.id}"

    def save(self, *args, **kwargs):
        """محاسبه خودکار حجم فایل هنگام ذخیره"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def increment_usage(self):
        """افزایش شمارنده استفاده از گیف"""
        self.usage_count += 1
        self.last_used = timezone.now()
        self.save()


class GIFTag(models.Model):
    """دسته‌بندی برای گیف‌ها"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ChatRoom(models.Model):
    """مدل اتاق چت با تمام ویژگی‌های پیشرفته"""

    TYPE_CHOICES = (
        ('PV', 'Private Chat'),
        ('GP', 'Group'),
        ('CH', 'Channel'),
        ('BC', 'Broadcast'),
    )

    # اطلاعات پایه
    name = models.CharField(max_length=255)
    username = models.SlugField(max_length=32, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    created_by = models.ForeignKey(User, related_name='created_chats', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(upload_to='chat_avatars/', null=True, blank=True)

    # تنظیمات حریم خصوصی
    is_public = models.BooleanField(default=False)
    invite_link = models.CharField(max_length=50, unique=True, null=True, blank=True)
    join_by_request = models.BooleanField(default=False)

    # تنظیمات رسانه
    sticker_set = models.ForeignKey(StickerPack, null=True, blank=True, on_delete=models.SET_NULL)
    gif_search_enabled = models.BooleanField(default=True)

    # آمار
    member_count = models.PositiveIntegerField(default=1)
    message_count = models.PositiveBigIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['username']),
            models.Index(fields=['invite_link']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"
    #
    # @property
    # def last_message_date(self):
    #     message_date = self.messages.filter(is_deleted=False).order_by('-date').first()
    #     if message_date:
    #         return message_date.date
    #     else:
    #         return None


class Participant(models.Model):
    """مدل شرکت‌کنندگان با سطوح دسترسی پیشرفته"""

    ROLE_CHOICES = (
        ('OW', 'Owner'),
        ('AD', 'Admin'),
        ('MO', 'Moderator'),
        ('ME', 'Member'),
        ('RE', 'Restricted'),
        ('BA', 'Banned'),
    )

    PERMISSION_CHOICES = (
        ('change_info', 'تغییر اطلاعات گروه'),
        ('post_messages', 'ارسال پیام'),
        ('edit_messages', 'ویرایش پیام‌ها'),
        ('delete_messages', 'حذف پیام‌ها'),
        ('ban_users', 'مسدود کردن کاربران'),
        ('invite_users', 'دعوت کاربران'),
        ('pin_messages', 'سنجاق کردن پیام‌ها'),
        ('add_admins', 'اضافه کردن ادمین'),
        ('anonymous', 'ارسال ناشناس'),
        ('manage_call', 'مدیریت تماس‌ها'),
        ('manage_stickers', 'مدیریت استیکرها'),
        ('post_gifs', 'ارسال گیف'),
    )

    user = models.ForeignKey(User, related_name='participations', on_delete=models.CASCADE)
    chat = models.ForeignKey(ChatRoom, related_name='participants', on_delete=models.CASCADE)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES, default='ME')
    joined_date = models.DateTimeField(auto_now_add=True)
    until_date = models.DateTimeField(null=True, blank=True)

    # دسترسی‌های سفارشی برای ادمین‌ها
    permissions = models.JSONField(default=list)

    # محدودیت‌ها
    is_muted = models.BooleanField(default=False)
    can_send_messages = models.BooleanField(default=True)
    can_send_media = models.BooleanField(default=True)
    can_send_polls = models.BooleanField(default=True)
    can_send_stickers = models.BooleanField(default=True)
    can_send_gifs = models.BooleanField(default=True)

    # اطلاعات اضافی
    custom_title = models.CharField(max_length=16, blank=True)

    class Meta:
        unique_together = ('user', 'chat')
        indexes = [
            models.Index(fields=['user', 'chat']),
            models.Index(fields=['chat', 'role']),
        ]

    def __str__(self):
        return f"{self.user} in {self.chat} as {self.get_role_display()}"


class Message(models.Model):
    """مدل پیام با پشتیبانی کامل از استیکر، گیف و رسانه"""

    TYPE_CHOICES = (
        ('text', 'Text'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('voice', 'Voice Message'),
        ('document', 'Document'),
        ('sticker', 'Sticker'),
        ('gif', 'GIF'),
        ('poll', 'Poll'),
        ('contact', 'Contact'),
        ('location', 'Location'),
        ('game', 'Game'),
        ('invoice', 'Invoice'),
        ('dice', 'Dice'),
    )

    chat = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.SET_NULL, null=True)
    sender_chat = models.ForeignKey(ChatRoom, related_name='channel_messages', on_delete=models.SET_NULL, null=True,
                                    blank=True)

    # محتوای پیام
    message_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')
    text = models.TextField(blank=True, validators=[MaxLengthValidator(4096)])
    caption = models.TextField(blank=True, validators=[MaxLengthValidator(1024)])
    entities = models.JSONField(default=list)

    # رسانه
    media_file = models.FileField(upload_to='chat_media/', null=True, blank=True)
    media_thumbnail = models.ImageField(upload_to='chat_thumbnails/', null=True, blank=True)

    # استیکر و گیف
    sticker = models.ForeignKey(Sticker, null=True, blank=True, on_delete=models.SET_NULL)
    gif = models.ForeignKey(GIF, null=True, blank=True, on_delete=models.SET_NULL)

    # ویژگی‌های پیام
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    is_pinned = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    edit_date = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    forwards = models.PositiveIntegerField(default=0)
    forward_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='forwarded_messages')

    # زمان‌ها
    date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)

    # تنظیمات پیام
    has_spoiler = models.BooleanField(default=False)
    is_silent = models.BooleanField(default=False)
    via_bot = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='bot_messages')

    # وضعیت پیام
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                   related_name='deleted_messages')
    delete_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['chat', 'date', 'id']),
            models.Index(fields=['sender', 'date']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['sticker']),
            models.Index(fields=['gif']),
        ]

    def __str__(self):
        return f"Message in {self.chat} by {self.sender or self.sender_chat}"

    def save(self, *args, **kwargs):
        """به‌روزرسانی خودکار نوع پیام بر اساس محتوا"""
        if self.sticker:
            self.message_type = 'sticker'
        elif self.gif:
            self.message_type = 'gif'
        super().save(*args, **kwargs)

    def increment_view_count(self, user):
        """افزایش تعداد مشاهده پیام"""
        self.views += 1
        self.save()
        MessageView.objects.get_or_create(message=self, user=user)

    def increment_forward_count(self):
        """افزایش تعداد فوروارد"""
        self.forwards += 1
        self.save()


class MessageReaction(models.Model):
    """واکنش‌ها به پیام"""

    REACTION_TYPES = (
        ('emoji', 'Emoji'),
        ('sticker', 'Custom Emoji (Sticker)'),
    )

    message = models.ForeignKey(Message, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reactions', on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    emoji = models.CharField(max_length=10, blank=True, null=True)
    sticker = models.ForeignKey(Sticker, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'emoji', 'sticker')
        indexes = [
            models.Index(fields=['message', 'user']),
        ]

    def __str__(self):
        return f"Reaction by {self.user} on {self.message.id}"


class MessageView(models.Model):
    """مشاهده پیام‌ها"""

    message = models.ForeignKey(Message, related_name='message_views', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='viewed_messages', on_delete=models.CASCADE)
    view_date = models.DateTimeField(auto_now_add=True)
    device = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('message', 'user')

    def __str__(self):
        return f"View by {self.user} on {self.message.id}"


class StickerUsage(models.Model):
    """آمار استفاده از استیکرها"""

    sticker = models.ForeignKey(Sticker, related_name='usage_stats', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='sticker_usages', on_delete=models.CASCADE)
    chat = models.ForeignKey(ChatRoom, related_name='sticker_usages', on_delete=models.CASCADE, null=True, blank=True)
    usage_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sticker']),
            models.Index(fields=['user']),
            models.Index(fields=['chat']),
        ]

    def save(self, *args, **kwargs):
        """افزایش شمارنده استفاده از استیکر"""
        super().save(*args, **kwargs)
        self.sticker.increment_usage()


class GIFUsage(models.Model):
    """آمار استفاده از گیف‌ها"""

    gif = models.ForeignKey(GIF, related_name='usage_stats', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='gif_usages', on_delete=models.CASCADE)
    chat = models.ForeignKey(ChatRoom, related_name='gif_usages', on_delete=models.CASCADE, null=True, blank=True)
    usage_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['gif']),
            models.Index(fields=['user']),
            models.Index(fields=['chat']),
        ]

    def save(self, *args, **kwargs):
        """افزایش شمارنده استفاده از گیف"""
        super().save(*args, **kwargs)
        self.gif.increment_usage()


class UserStickerCollection(models.Model):
    """مجموعه استیکرهای کاربر"""

    user = models.ForeignKey(User, related_name='sticker_collections', on_delete=models.CASCADE)
    pack = models.ForeignKey(StickerPack, related_name='user_collections', on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'pack')
        indexes = [
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return f"{self.pack.title} for {self.user}"


class UserGIFCollection(models.Model):
    """مجموعه گیف‌های کاربر"""

    user = models.ForeignKey(User, related_name='gif_collections', on_delete=models.CASCADE)
    gif = models.ForeignKey(GIF, related_name='user_collections', on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'gif')
        indexes = [
            models.Index(fields=['user', 'is_favorite']),
        ]

    def __str__(self):
        return f"GIF {self.gif.id} for {self.user}"


class StickerSearchLog(models.Model):
    """لاگ جستجوی استیکر"""

    user = models.ForeignKey(User, related_name='sticker_searches', on_delete=models.CASCADE)
    query = models.CharField(max_length=100)
    results_count = models.PositiveIntegerField()
    search_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'search_date']),
        ]


class GIFSearchLog(models.Model):
    """لاگ جستجوی گیف"""

    user = models.ForeignKey(User, related_name='gif_searches', on_delete=models.CASCADE)
    query = models.CharField(max_length=100)
    results_count = models.PositiveIntegerField()
    search_date = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, blank=True)  # منبع جستجو (GIPHY, Tenor, etc.)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'search_date']),
        ]


class AdminLog(models.Model):
    """لاگ اقدامات ادمین‌ها"""

    ACTION_CHOICES = (
        ('change_info', 'تغییر اطلاعات گروه'),
        ('edit_message', 'ویرایش پیام'),
        ('delete_message', 'حذف پیام'),
        ('ban_user', 'مسدود کردن کاربر'),
        ('invite_user', 'دعوت کاربر'),
        ('pin_message', 'سنجاق پیام'),
        ('promote_admin', 'ترفیع به ادمین'),
        ('demote_admin', 'تنزل از ادمین'),
        ('toggle_admin', 'تغییر دسترسی ادمین'),
    )

    chat = models.ForeignKey(ChatRoom, related_name='admin_logs', on_delete=models.CASCADE)
    actor = models.ForeignKey(User, related_name='admin_actions', on_delete=models.CASCADE)
    action = models.CharField(max_length=15, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                    related_name='admin_logs_against')
    details = models.JSONField(default=dict)  # جزئیات اقدام
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.actor} {self.get_action_display()} in {self.chat}"
