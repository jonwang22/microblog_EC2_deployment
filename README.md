# Micro Blog Application
---
## Purpose - Self-Managed Application and Monitoring

In the previous exercises, we deployed a flask app using Elastic Beanstalk. Now we're going to deploy our app manually to our EC2 instance and then set up a monitoring server to pull metrics from the app server to track system metrics.

This module will provide a more hands on approach in the inner workings of what Elastic Beanstalk did for us where we will now need to perform the steps manually or through scripts as we won't have Elastic Beanstalk doing that setup for us. 

## Steps Taken to Implement

### <ins>Set Up Our Environment</ins>

For this project, we're going to create a "Jenkins" server that will run our application and host it for internet traffic. We need to install Jenkins to perform our CI/CD automation, Python3.9 for our code interpreter, Python3.9-venv to be able to create virtual envs using Python3.9, python3-pip to install the python3 package manager, nginx for our reverse proxy server, and node-exporter to grab our server metrics. 

We will also need to create a "Monitoring" server and install Prometheus and Grafana to create a operations dashboard. 

For our Application, we'll need to create an empty repository in GitHub, clone the source repository, and push it to the working repository.

#### <ins>Clone Source Code Repo</ins>
First, let's clone the application source code repository. We can use any Amazon EC2 Linux box in the AWS account or we can do this locally on your laptop.
* Clone source application repo to new github repository. Our Source Repository was [cloned from here.](https://github.com/kura-labs-org/C5-Deployment-Workload-3)
   ```
   git clone $SOURCE_REPO_LINK #Cloning source repo to local machine or instance
   git remote rename origin upstream #We are renaming the current remote origin to be called upstream
   git remote add origin $DESTINATION_REPO_LINK #Setting new repo as our remote origin
   git push origin main #Now we push the repo to the new repo using main branch (sometimes branch is master)
   ```
   * The reason why we want to clone the source repo and push it to our new repo is so we can have ownership of our working repository and make commits as needed and not mess with the source repository. This may be necessary when we may not have the necessary permissions to interact and commit to the source repository and we need to pull application code for our personal use. The reason why we aren't forking the repository is so we can track our commits and changes.

#### <ins>Setup Jenkins and Monitoring Instances</ins>
We need to create our EC2 instances now. For this workload we'll attempt to use t3.micro instance types for both instances. 

<ins>Jenkins Server</ins>

1. Create the t3.micro and name it "Jenkins" (We'll also be using this as our application server because we'll need to install python, nginx, and some other software to it.)
2. We need to configure our Security group to allow SSH(port 22), HTTP(port 80), Jenkins(port 8080), and Node-Exporter(port 9100) from all sources.
3. We'll need to install a few software for this which includes Jenkins (CI/CD tool), Python 3.9 (code interpreter), Python3.9-venv (virtual environment module), python3-pip (python package manager), and nginx (reverse proxy that redirects http requests to the application port), and node-exporter (grabs server metrics). If you'd like to see the script used to install these components, [you can find it here](https://github.com/jonwang22/microblog_EC2_deployment/blob/main/setup_resources/install_resources.sh). Make sure the script is executable first with ```$chmod +x ~/microblog_EC2_deployment/setup_resources/install_resources.sh```.

<ins>Monitoring Server</ins>

1. Create the t3.micro and name it "Monitoring", we will need to install Prometheus and Grafana. Prometheus is going to retrieve metrics from connected Node-Exporter. Grafana is going to pull the metrics from Prometheus and graph them so we can create dashboards to monitor our application server.
2. We need to configure a new security group for the "Monitoring" server. The group should allow SSH(port 22), Prometheus(port 9090), and Grafana(port 3000).
3. Install Prometheus and Grafana. You can use this script to install Prometheus and Grafana as well as configure Prometheus to access the target to Node-Exporter on the application server. You can find the [installation script here](https://github.com/jonwang22/microblog_EC2_deployment/blob/main/setup_resources/install_prometheus_grafana.sh). Make sure the script is executable first with ```$chmod +x ~/microblog_EC2_deployment/setup_resources/install_prometheus_grafana.sh```

Now that we have created our instances, we can move on to testing our application and making sure it works before we automate the process.

### <ins>Manually Building/Testing Application</ins>
We can now begin manually testing our application and making sure it works before we use Jenkins to automate our CI/CD pipeline. 

1. Let's clone our working directory to our "Jenkins" instance and navigate to the folder directory.
    ```
    $git clone https://github.com/jonwang22/microblog_EC2_deployment.git && cd microblog_EC2_deployment
    ```
2. Now we can create our virtual python environment to create an isolated environment for our application to run in free of any potential conflicting dependencies.
    ```
    $python3.9 -m venv venv
    $source venv/bin/activate
    ```
3. Once we're in our virtual environment, we can now install all our application dependencies. We may also need to upgrade pip in case it is out of date.
    ```
    $pip install --upgrade pip
    $pip install -r requirements.txt
    $pip install gunicorn pymysql cryptography
    ```
    Here we're installing "gunicorn" which is our WSGI(Web Server Gateway Interface) or also known as Python web server, "pymysql" is our database, "cryptography" provides cryptographic recipes and primitives to Python. We also have a list of application dependencies within "requirements.txt" and all of those dependencies are installed.
4. Set Environment Variable for FLASK_APP
    ```
    $export FLASK_APP=microblog.py
    ```
    We are exporting FLASK_APP variable with 'microblog.py' because for our future flask commands that we run, flask needs to know what application to load. We could use the '--app' flag as well with the 'microblog.py' following it in the command line but exporting the variable allows us to use that app designation in other areas that we need, especially during our Jenkins pipeline.
5. Now we can run our flask commands to build our app.
    ```
    $flask translate compile
    $flask db upgrade
    ```
    `flask translate compile` is translating human readable files into binary files that can be read efficiently by the application. `flask db upgrade` applies migration scripts to actual database and updates the schema to match the current models.
6. We now need to configure our NGINX configuration file so that NGINX knows where to forward http requests from port 80. NGINX helps redirect the traffic from port 80 to port 5000 where the application is hosted.
    ```
    location / {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    ```
7. Lastly we'll start up our gunicorn web server so we can see if our application is up and running.
    ```
    $gunicorn -b :5000 -w 4 microblog:app
    ```
    This command is starting up the gunicorn web server that will front our application bound on port 5000. We will create 4 worker processes for the app to handle incoming requests. More worker processes helps the app's ability to handle more traffic. `microblog:app` tells gunicorn to look for the module 'microblog' and search for the app object 'app' and then run it.

    When you put the app server public IP into the browser, nginx is rerouting your HTTP 80 request to the application port 5000 so you can see the application and interact with it. Gunicorn is hosting that web application on port 5000. The reason why we don't need to explicitly add port 5000 on our security group is because the routing happens internally within the host through NGINX so all we need to allow traffic through is port 80.

### <ins>Automate Pipeline with Jenkins</ins>
Now that we tested our application and made sure it works manually, we can now start implementing our automation with Jenkins to build, test, perform checks, clean up and deploy our application.

#### <ins>Configuring Jenkins Multi-Branch Pipeline</ins>

Let's configure out Jenkins file first, we need to define the "Build" stage with commands we need to run as well as our "Deploy" stage. We will also need to create some unit tests for our "Test" stage in Jenkinsfile.

Before we dive into the `Jenkinsfile` we'll need to create our Multi-Branch pipeline in Jenkins and connect it to our Github repo. We'll need to use our username and personal access token again to authorize that connection so Jenkins can pull our working github repo.

<ins>Build Stage</ins>

This is our "Build" stage in Jenkins. We are essentially taking the commands that we ran manually to set up our environment to run our application. These commands will allow Jenkins to build out our environment within the python venv.
```
    pipeline {
      agent any
        stages {
            stage ('Build') {
                steps {
                    sh '''#!/bin/bash
                    python3.9 -m venv venv
		            source venv/bin/activate
		            pip install --upgrade pip
		            pip install -r requirements.txt
		            pip install gunicorn pymysql cryptography
		            export FLASK_APP=microblog.py
		            flask translate compile
		            flask db upgrade
		            '''
                }
            }
```
![image](https://github.com/user-attachments/assets/1504b343-5b1a-4ced-a5b5-2722f40e72ce)

<ins>Test Stage</ins>

For our "Test" Stage, we need a unit test. We're going to create a `test_app.py` file in `microblog_EC2_deployment/tests/unit` folder. We will keep it simple just to make sure the test stage works well. For optimization purposes, we'll want to make sure we have unit tests that test every unit of code within our application to make sure we have full code coverage and be confident that our application will work without issues in the current deployment. 

Unit Test in `test_app.py`
```
# Unit Testing
import pytest
import sys
import os
sys.path.append(os.getcwd())
from microblog import app

# Testing website HTTP Get requests
@pytest.fixture
def client():
    app.config.update({"TESTING": True,})
    return app.test_client()

def test_website(client):
    response = client.get("/", follow_redirects = True)
    assert response.status_code == 200
```
Here we are just testing to see if we can reach the login page of our application.

Our Jenkinsfile has the "Test" Stage which will use this `test_app.py` file to run our unit tests.
```
            stage ('Test') {
                steps {
                    sh '''#!/bin/bash
                    source venv/bin/activate
                    py.test ./tests/unit/ --verbose --junit-xml test-reports/results.xml
                    '''
                }
                post {
                    always {
                        junit 'test-reports/results.xml'
                    }
                }
            }
```

![image](https://github.com/user-attachments/assets/a2b8bb31-74ae-48ac-898a-fdaaeead38c3)

<ins>OWASP FS SCAN Stage</ins>

This stage is performing dependency security vulnerability scans by checking against the NVD (National Vulnerability Database). In order for Jenkins to properly connect and perform this check, we need to install the OWASP Dependency-Check plugin to Jenkins. 

The reason why we need this step is because we want to make sure our dependencies are using any versions that may have CVEs (Common Vulnerability and Exposures) that could compromise our application security. This scan helps us determine if we need to use a different dependency or potentially upgrade our dependency to a more secure version. The plugin is important because it integrates the OWASP Dependency-Check tool into Jenkins, allowing automatic scans of our software during the pipeline.

To install the plugin,

* Navigate to "Manage Jenkins" > "Plugins" > "Available plugins" > Search and install

* Then configure it by navigating to "Manage Jenkins" > "Tools" > "Add Dependency-Check > Name: "DP-Check" > check "install automatically" > Add Installer: "Install from github.com"

```
            stage ('OWASP FS SCAN') {
                steps {
                    dependencyCheck additionalArguments: '--scan ./ --disableYarnAudit --disableNodeAudit', odcInstallation: 'DP-Check'
                    dependencyCheckPublisher pattern: '**/dependency-check-report.xml'
                }
            }
```

NOTE: This step took a very long time and ate a lot of resources on the instance, had to upgrade Jenkins server to t3.medium due to resource constraints.

![image](https://github.com/user-attachments/assets/09778cb8-4933-4a49-a12b-57e3e5aacb54)

<ins>Clean Stage</ins>

This stage is to clean up any existing app processes that may be running prior to deploying and launching the latest application.

```
            stage ('Clean') {
                steps {
                    sh '''#!/bin/bash
                    if [[ $(ps aux | grep -i "gunicorn" | tr -s " " | head -n 1 | cut -d " " -f 2) != 0 ]]
                    then
                    ps aux | grep -i "gunicorn" | tr -s " " | head -n 1 | cut -d " " -f 2 > pid.txt
                    kill $(cat pid.txt)
                    exit 0
                    fi
                    '''
                }
            }
```

Here we're looking for the first instance of gunicorn within our running processes list, grabbing the PID, storing that in a pid.txt file and then killing that process. The process that should be obtained is the main gunicorn process and not the worker processes. There is room for optimization here especially with the current setup that we're working with now that we have gunicorn as a systemd service. We would most likely change this script to just say ```sudo /bin/systemctl stop gunicorn``` to stop the service before restarting it in the "Deploy" Stage.

![image](https://github.com/user-attachments/assets/616d2a7b-51c1-4007-a71a-99039afc3ba7)

<ins>Deploy Stage</ins>

Our "Deploy" stage is not as simple as our "Build". The reason is because if we just use the same command to execute our web server, `gunicorn -b :5000 -w 4 microblog:app`, then the Jenkins pipeline will not finish. (More on this in the Troubleshooting section later on in this README).
```
            stage ('Deploy') {
                steps {
                    sh '''#!/bin/bash
                    source venv/bin/activate
		            sudo /bin/systemctl restart gunicorn
		            if sudo /bin/systemctl is-active --quiet gunicorn; then
		                echo "Gunicorn restarted successfully."
		            else
		                echo "Failed to restart Gunicorn."
		                sudo /bin/journalctl -u gunicorn.service
		                exit 1
		            fi
                    '''
                }
            }
```

Instead we need to create a systemd service for gunicorn and have our application run as a system service in the background. The reason why we want it to run as a systemd service is because we want our application to run in the background and persist after the Jenkins build and deployment. If we just run it in the background, then Jenkins pipeline will complete, and we won't be able to access our application because Jenkins kills it to complete its actions. If we give Jenkins permissions to run our `systemctl` commands with sudo permissions, then we will be able to execute our deployment and deploy and run our application.

With that said, we need to also configure our `/etc/sudoers.tmp` file.
```
sudo visudo
```
We then add the following to this file under User privilege specification
```
jenkins ALL=(ALL:ALL) NOPASSWD: /bin/systemctl restart gunicorn
jenkins ALL=(ALL:ALL) NOPASSWD: /bin/systemctl is-active --quiet gunicorn
jenkins ALL=(ALL:ALL) NOPASSWD: /bin/journalctl -u gunicorn.service
```

![image](https://github.com/user-attachments/assets/5b0c55e2-819b-440b-8ce9-09120cea0111)

This is so that we can allow Jenkins to run these sudo commands without passwords. If we do not set it up this way, then Jenkins will not be allowed to perform these commands and the deployment will fail. Here is our successful deployment.

![image](https://github.com/user-attachments/assets/452afecb-c618-45f4-82fc-e71225f46167)


Here is the build pipeline from Jenkins
![image](https://github.com/user-attachments/assets/ed5ae076-683a-42bd-8d5a-52aebeacf98f)

<ins>Check Application on Web Browser</ins>

After deployment is successful, we will need to check our endpoint and make sure we can access our web app. When we input our public IP into our browser it should bring us to the login page below.

![image](https://github.com/user-attachments/assets/84744bfa-8ebf-4ebf-a0c7-fe2b7dbb7080)

### <ins>Configuring Monitoring Dashboard in Grafana</ins>
We've already done the initial setup to configure Prometheus to obtain our metrics from the node-exporter on our app server. Now we need to configure Grafana to pull the Prometheus Data Source and build our dashboard.

1. Create a new dashboard in Grafana and 'Add Visualization'
2. Select a data source, if none, then create a data source from Prometheus. In order to maintain connection between Grafana and Prometheus, you'll need to use the Private IP of the Prometheus server. This works because the instance is in the same VPC and Grafana and Prometheus are on the same instance.
3. Once you create your data source you can now build your dashboard. Below are some images of the dashboard I created, I selected some metrics that I saw could be of importance for us when we're monitoring our application server.
![image](https://github.com/user-attachments/assets/29f2d878-ad06-45da-963c-59bf3d921a85)
![image](https://github.com/user-attachments/assets/f9456f4f-0727-4144-a78b-21050a8dfbee)

## System Design
![image](https://github.com/user-attachments/assets/3719c5d3-da99-4c78-ab18-f3d5e2e6a761)

## Issues/Troubleshooting

Ran into a lot of issues with this deployment but was able to overcome them. Below is a list of them
1. Pytest, creating the pytest was an issue for me because I'm not familiar with creating unit tests. This is an item that I want to work on and improve in writing.
2. OWASP FS Scan on t3.micro took a very long time. I should've figured out that I may need more resources to finish the scans quickly with a bigger instance. Ended up moving to a t3.medium.
3. Deploy Stage. I had a lot of issues figuring out how to get the process to run in the background and persist. I eventually found a way to create a systemd service for gunicorn and ran it that way.
 

## Optimization

There's multiple areas for optimization. The obvious areas are with the Jenkinsfile and PyTest. When we're setting up our Jenkins instance by installing all of the necessary tools and dependencies necessary before we execute, besides using a script to manually install it everytime, I'm thinking there has to be a way to perform that across an entire fleet of hosts. Maybe there's a way we can include an installation script within the package and tell Jenkins to run that installation script and then setup the virtual environment for our python application.

With Pytest, the optimization is adding more unit tests for full code coverage where possible, testing every aspect of code. This is an area that I need to learn more about and improve in and get comfortable with. 

Infrastructure wise, since we are not using Elastic Beanstalk, we have to manage our own resources and we need to be aware of our instances and how our application is performing or how our CI/CD pipeline is performing with the resources we're using. Do we need to use more resources? Do we need more instances to host our application? These are some things to think about when we are manually managing our system architecture instead of relying on a managed service like AWS Elastic Beanstalk.

## Conclusion

This exercise was a really good introduction in what its like to manually maintain and deploy your application to your own resources in the cloud. You have full control of what you do and how its done however there are a lot of areas that can cause issues. Services like AWS Elastic Beanstalk help take the difficulties and headaches away at a cost for the service but it doesn't provide as much flexibility as managing your own infrastructure does.
