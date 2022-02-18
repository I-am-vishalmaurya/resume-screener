from django.urls import path

from .views import UploadResume, HRJobPost, JobListView, ApplyForJob, AppliedCandidates, HRJobPostView, resume_download

app_name = 'resumes'

urlpatterns = [
    path('upload', UploadResume, name='upload_resume'),
    path('job', HRJobPost, name='hr_job_postings'),
    path('jobs', JobListView, name='job_listings'),
    path('apply/<int:job_id>', ApplyForJob, name='apply_for_job'),
    path('your-jobs', HRJobPostView, name='your_jobs'),
    path('applied-candidates/<int:job_id>', AppliedCandidates, name='applied_candidates'),
    path('download/<int:user_id>', resume_download, name='download_resume'),

]