import mimetypes
import os

from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib import messages
# import Auth model
from django.contrib.auth.models import User
from .models import CandidateResumes, HRJobPostings, AppliedJobs
import PyPDF2
import spacy


# Create your views here.

nlp = spacy.load("en_core_web_sm")
skill_pattern_path = os.path.join(settings.BASE_DIR, 'resumes/skill_patterns.jsonl')
ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(skill_pattern_path)


def resume_download(request, user_id):
    candidate_resume = CandidateResumes.objects.get(user_id=user_id)
    file_path = os.path.join(settings.MEDIA_ROOT, candidate_resume.resume_file.name)
    f = open(file_path, "rb")
    mime_type, _ = mimetypes.guess_type(file_path)
    print(mime_type)
    # Set the return value of the HttpResponse
    response = HttpResponse(f, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % candidate_resume.resume_file.name
    return response


def get_skills(text):
    doc = nlp(text)
    myset = []
    subset = []
    for ent in doc.ents:
        if ent.label_ == "SKILL" or ent.label_ == "SKILLS":
            subset.append(ent.text)
    myset.append(subset)
    return subset


def unique_skills(x):
    return list(set(x))


def listToString(s):
    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele + ","

    # return string
    return str1


def matchSkills(resume, job_skills):
    job_skill = listToString(job_skills)
    print("Job Skill is: ", job_skill)
    req_skills = job_skill.lower().split(',')
    print("Required Skills are: ", req_skills)
    resume_skills = unique_skills(get_skills(resume.lower()))
    print("Resume Skills are: ", resume_skills)
    score = 0
    for x in req_skills:
        if x in resume_skills:
            score += 1
    req_skills_len = len(req_skills)
    match = round(score / req_skills_len * 100, 1)

    print(f"The current Resume is {match}% matched to your requirements")
    return match


def HRJobPostView(request):
    if request.method == 'GET':
        job_list = HRJobPostings.objects.filter(user=request.user)
        return render(request, 'resumes/hr_job_post.html', {'job_list': job_list})


def AppliedCandidates(request, job_id):
    if request.method == 'GET':
        applied_candidates = AppliedJobs.objects.filter(job_posting_id=job_id).select_related('candidate')
        users = []
        resumes = []
        for user in applied_candidates:
            users.append(user.candidate.user_id)
            resumes.append(user.candidate.resume_file)
        # get matching skills
        job_skills = HRJobPostings.objects.get(id=job_id).skills_required.split(',')
        match_percentage = []
        for resume in resumes:
            pdffileobj = open(os.path.join(settings.MEDIA_ROOT, str(resume)), 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdffileobj)
            x = pdfReader.numPages
            print("Number of pages is", x)
            pageObj = pdfReader.getPage(x - 1)
            text = pageObj.extractText()
            match_percentage.append(matchSkills(text, job_skills))
        user_details = User.objects.filter(id__in=users)
        final = []
        for user in user_details:
            final.append({'id': user.id, 'name': user.first_name + ' ' + user.last_name, 'email': user.email,
                          'resume': resumes[users.index(user.id)],
                          'matching_percentage': match_percentage[users.index(user.id)]})
        print(final)
        return render(request, 'resumes/applied_candidates.html', {'all_details': final})


def UploadResume(request):
    if request.method == 'GET':
        return render(request, 'resumes/upload_resume.html')

    if request.method == 'POST':
        resume = request.FILES['resume']
        allowed_extension = settings.ALLOWED_EXTENSIONS
        if resume.name.split('.')[-1] in allowed_extension:
            if CandidateResumes.objects.filter(user=request.user).exists():
                CandidateResumes.objects.get(user=request.user).delete()
                CandidateResumes.objects.create(user=request.user, resume_file=resume)
                messages.success(request, 'Resume Updated successfully')
                return render(request, 'resumes/upload_resume.html', {'message': 'Resume updated successfully'})
            else:
                CandidateResumes(
                    user=request.user,
                    resume_file=resume).save()

                messages.success(request, 'Resume uploaded successfully')
                return render(request, 'resumes/upload_resume.html', {'message': 'Resume uploaded successfully'})
        else:
            messages.error(request, 'Please upload a valid PDF, or word file')


def JobListView(request):
    if request.method == 'GET':
        job_list = HRJobPostings.objects.all()
        return render(request, 'resumes/job_list.html', {'job_list': job_list})


def ApplyForJob(request, job_id):
    if request.method == 'GET':
        job = HRJobPostings.objects.get(id=job_id)
        candidate = CandidateResumes.objects.get(user=request.user)
        # check if already applied for job
        if AppliedJobs.objects.filter(candidate=candidate, job_posting=job).exists():
            messages.warning(request, 'You have already applied for this job')
            return render(request, 'resumes/job_list.html', {'message': 'You already applied for this job'})
        else:
            AppliedJobs(
                job_posting=job,
                candidate=candidate,
            ).save()
            messages.success(request, 'You have successfully applied for the job')
            return render(request, 'resumes/job_list.html', {'message': 'You have successfully applied for the job'})
    else:
        messages.error(request, 'You are not authorized to apply for the job')
        return render(request, 'resumes/job_list.html', {'message': 'You are not authorized to apply for the job'})


def HRJobPost(request):
    if request.method == 'GET':
        return render(request, 'resumes/add_job_posting.html')
    elif request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        location = request.POST['location']
        skills = request.POST['skills']

        if request.user.is_staff:
            HRJobPostings(
                job_title=title,
                job_description=description,
                job_location=location,
                skills_required=skills,
                user=request.user).save()
            messages.success(request, 'Job posting added successfully')
            return render(request, 'resumes/add_job_posting.html', {'message': 'Job posting added successfully'})
        else:
            messages.error(request, 'You are not authorized to add job postings')
            return render(request, 'resumes/add_job_posting.html', {'message': 'You are not authorized to add job '
                                                                               'postings'})
