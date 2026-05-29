from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Course, Enrollment, Question, Choice, Submission
from django.contrib.auth.models import User
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging

logger = logging.getLogger(__name__)

# -------------------------
# Registration / Login / Logout
# -------------------------
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
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
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)

def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')

# -------------------------
# Enrollment check
# -------------------------
def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled

# -------------------------
# Course list / detail
# -------------------------
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'

# -------------------------
# Enrollment
# -------------------------
def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if not check_if_enrolled(user, course) and user.is_authenticated:
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()
    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))

# -------------------------
# Extract answers from POST
# -------------------------
def extract_answers(request):
    submitted_answers = []
    for key in request.POST:
        if key.startswith('choice'):
            choice_id = int(request.POST[key])
            submitted_answers.append(choice_id)
    return submitted_answers

# -------------------------
# Submit exam
# -------------------------
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = get_object_or_404(Enrollment, user=user, course=course)

    # Create submission
    submission = Submission.objects.create(enrollment=enrollment)
    selected_choices = extract_answers(request)
    submission.choices.set(selected_choices)
    submission.save()

    return HttpResponseRedirect(reverse('onlinecourse:exam_result', args=(course.id, submission.id)))

# -------------------------
# Show exam result
# -------------------------
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    choices = submission.choices.all()

    total_score = 0
    questions_results = []

    for question in course.question_set.all():
        correct_choices = set(question.choice_set.filter(is_correct=True))
        selected_choices = set(choices.filter(question=question))
        got_score = correct_choices == selected_choices
        grade = question.grade if got_score else 0
        total_score += grade
        questions_results.append({
            'question': question,
            'got_score': got_score,
            'grade': grade
        })

    context = {
        'course': course,
        'submission': submission,
        'choices': choices,
        'total_score': total_score,
        'questions_results': questions_results
    }

    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)