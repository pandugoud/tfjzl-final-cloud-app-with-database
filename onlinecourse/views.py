from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.views import generic
from django.contrib.auth import login, logout, authenticate

# -------------------------
# AUTH: Registration, Login, Logout
# -------------------------
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)

    username = request.POST['username']
    password = request.POST['psw']
    first_name = request.POST['firstname']
    last_name = request.POST['lastname']

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
        login(request, user)
        return redirect("onlinecourse:index")
    else:
        context['message'] = "User already exists."
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid credentials"
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')

# -------------------------
# Enrollment helper
# -------------------------
def check_if_enrolled(user, course):
    return Enrollment.objects.filter(user=user, course=course).exists()

# -------------------------
# Course List and Detail
# -------------------------
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        courses = Course.objects.order_by('-total_enrollment')[:10]
        user = self.request.user
        for course in courses:
            course.is_enrolled = user.is_authenticated and check_if_enrolled(user, course)
        return courses

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        user = self.request.user
        course.is_enrolled = user.is_authenticated and check_if_enrolled(user, course)
        context['course'] = course
        return context

# -------------------------
# Enroll
# -------------------------
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.is_authenticated and not check_if_enrolled(request.user, course):
        Enrollment.objects.create(user=request.user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))

# -------------------------
# Exam Page
# -------------------------
def exam(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    questions = course.question_set.all()
    return render(request, 'onlinecourse/exam.html', {
        'course': course,
        'questions': questions
    })

# -------------------------
# Submit Exam
# -------------------------
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)

    submission = Submission.objects.create(enrollment=enrollment)
    selected_choices = [int(request.POST[key]) for key in request.POST if key.startswith('choice')]
    submission.choices.set(selected_choices)
    submission.save()

    return HttpResponseRedirect(
        reverse('onlinecourse:exam_result', args=(course.id, submission.id))
    )

# -------------------------
# Show Exam Result
# -------------------------
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    selected_choices = submission.choices.all()
    total_score = 0
    questions_results = []

    for question in course.question_set.all():
        correct_choices = set(question.choice_set.filter(is_correct=True).values_list('id', flat=True))
        selected = set(selected_choices.filter(question=question).values_list('id', flat=True))
        got_score = correct_choices == selected
        grade = question.grade if got_score else 0
        total_score += grade
        questions_results.append({
            'question': question,
            'got_score': got_score,
            'grade': grade
        })

    return render(request, 'onlinecourse/exam_result_bootstrap.html', {
        'course': course,
        'submission': submission,
        'choices': selected_choices,
        'total_score': total_score,
        'questions_results': questions_results
    })