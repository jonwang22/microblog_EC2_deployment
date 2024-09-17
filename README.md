# Micro Blog Application


---


## Purpose - Monitoring Application and Server Resources

In the previous exercises, we deployed a flask app using Elastic Beanstalk. Now we're going to deploy our app manually to our EC2 instance and then set up a monitoring server to pull metrics from the app server to track system metrics.

This module will provide a more hands on approach in the inner workings of what Elastic Beanstalk did for us where we will now need to perform the steps manually or through scripts as we won't have Elastic Beanstalk doing that setup for us.

## Steps Taken to Implement

1. Clone this repo to your GitHub account. IMPORTANT: Make sure that the repository name is "microblog_EC2_deployment"
   * Performed git clone, then modified the old remote to upstream and then set new remote to origin for the new repo and pushed to main origin for new repo to clone the source repo to the new one. We did this because we wanted to grab the resources from the source repository and have a completely separate repository to perform the work in. We want to track the changes we make to this repo and that's why we did not fork the repository.
//TODO ADD COMMANDS FOR DOING THIS
```
### ADD GIT CLONE STEPS HERE
```

2. We need to create our EC2 Instance. We'll be using t3.micro. For this application, we will be installing Jenkins (CI/CD tool), Python 3.9 (code interpreter), Python3.9-venv (virtual environment module), python3-pip (python package manager), and nginx (reverse proxy). We need Jenkins to build, test, perform checks on our application before we deploy it and have it in production. Python3.9 is what our application is written in and is the version compatible for our code. Python3-pip ensures we have a python package manager installed regardless of python version. Nginx is our reverse proxy that will point clients to the proper port where our application will be hosted. If you'd like to see the script used to install these components, [you can find it here](https://github.com/jonwang22/microblog_EC2_deployment/blob/main/install_jenkins.sh).


6. Clone your GH repository to the server, cd into the directory, create and activate a python virtual environment with: 
```
$python3.9 -m venv venv
$source venv/bin/activate
```

5. While in the python virtual environment, install the application dependencies and other packages by running:

```
$pip install -r requirements.txt
$pip install gunicorn pymysql cryptography
```

6. Set the ENVIRONMENTAL Variable:

```
FLASK_APP=microblog.py
```
Question: What is this command doing?

7. Run the following commands: 

```
$flask translate compile
$flask db upgrade
```

8. Edit the NginX configuration file at "/etc/nginx/sites-enabled/default" so that "location" reads as below.

```
location / {
proxy_pass http://127.0.0.1:5000;
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```
Question: What is this config file/NginX responsible for?

9. Run the following command and then put the servers public IP address into the browser address bar

```
gunicorn -b :5000 -w 4 microblog:app
```
Question: What is this command doing? You should be able to see the application running in the browser but what is happening "behind the scenes" when the IP address is put into the browser address bar?

10. If all of the above works, stop the application by pressing ctrl+c.  Now it's time to automate the pipeline.  Modify the Jenkinsfile and fill in the commands for the build and deploy stages.

  a. The build stage should include all of the commands required to prepare the environment for the application.  This includes creating the virtual environment and installing all the dependencies, setting variables, and setting up the databases.

  b. The test stage will run pytest.  Create a python script called test_app.py to run a unit test of the application source code. IMPORTANT: Put the script in a directory called "tests/unit/" of the GitHub repository. Note: The complexity of the script is up to you.  Work within your limits.  (Hint: If you don't know where to start, try testing the homepage or log in page.  Want to challenge yourself with something more complicated? Sky's the limit!)

  c. The deploy stage will run the commands required to deploy the application so that it is available to the internet. 

  d. There is also a 'clean' and an 'WASP FS SCAN' stage.  What are these for?
  
11. In Jenkins, install the "OWASP Dependency-Check" plug-in

    a. Navigate to "Manage Jenkins" > "Plugins" > "Available plugins" > Search and install

 	b. Then configure it by navigating to "Manage Jenkins" > "Tools" > "Add Dependency-Check > Name: "DP-Check" > check "install automatically" > Add Installer: "Install from github.com"

Question: What is this plugin for?  What is it doing?  When does it do it?  Why is it important?

12. Create a MultiBranch Pipeline and run the build.  IMPORTANT: Make sure the name of the pipeline is: "workload_3".

    Note: Did the pipeline complete? Is the application running?

    Hint: if the pipeline stage is unable to complete because the process is running, perhaps the process should be run in the BACKGROUND (daemon).
    
    Hint pt 2: NOW does the pipeline complete? Is the application running?  If not: What happened to that RUNNING PROCESS after the deploy STAGE COMPLETES? (stayAlive)

14. After the application has successfully deployed, create another EC2 (t3.micro) called "Monitoring".  Install Prometheus and Grafana and configure it to monitor the activity on the server running the application. 

15. Document! All projects have documentation so that others can read and understand what was done and how it was done. Create a README.md file in your repository that describes:

	  a. The "PURPOSE" of the Workload,

  	b. The "STEPS" taken (and why each was necessary/important),
      Question: Were steps 4-9 absolutely necessary for the CICD pipeline? Why or why not?
    
  	c. A "SYSTEM DESIGN DIAGRAM" that is created in draw.io (IMPORTANT: Save the diagram as "Diagram.jpg" and upload it to the root directory of the GitHub repo.),

	  d. "ISSUES/TROUBLESHOOTING" that may have occured,

  	e. An "OPTIMIZATION" section for that answers the question: What are the advantages of provisioning ones own resources over using a managed service like Elastic Beanstalk?  Could the infrastructure created in this workload be considered that of a "good system"?  Why or why not?  How would you optimize this infrastructure to address these issues?

    f. A "CONCLUSION" statement as well as any other sections you feel like you want to include.
