import requests


class UiPathConnection:

    """Base class for initial functions and storing authentication credentials"""

    def __init__(self, url, tenant, username, password, cloud=False, tenant_logical_name='', client_id='', user_key=''):

        """Initialize the class

        Keyword Arguments:
            url: URL of the orchestrator
            tenant: Name of tenant to connect to
            username: username of the admin
            password: password for the username

        NOTE: These parameters only need to be entered if you are on the cloud version of UiPath

            url: "https://platform.uipath.com/[Account Logical Name]/[Tenant Logical Name]"
            cloud: Needs to be set to True if this is the cloud platform
            tenant_logical_name: Can be found on the website for your tenant
            client_id: can be found on the website for your tenant
            user_key: can be found on the website


        """
        self.base_url = url
        self.tenant = tenant
        self.cloud = cloud
        self.tenant_logical_name = tenant_logical_name
        self.token = self._authenticate(username, password, tenant, tenant_logical_name, client_id, user_key)

    def _authenticate(self, username, password, tenant, tenant_logical_name, client_id, user_key):

        """Authenticate. This will store the token for future usage as the authentication method for UiPath Rest
        API is Bearer Token authentication.

        There are two types of authentication.  One for cloud environments and one for on-premise.  The following
        accounts for this.

        """

        if self.cloud:
            payload = str(
                {"grant_type": "refresh_token",
                 "client_id": client_id,
                 "refresh_token": user_key}
            )
            headers = {'content-type': 'application/json', 'X-UIPATH-TenantName': tenant_logical_name}
            url = 'https://account.uipath.com/oauth/token'
            r = requests.post(url, data=payload, headers=headers)
            print(r)

        else:
            payload = str(
                    {"tenancyName": tenant,
                     "usernameOrEmailAddress": username,
                     "password": password}
                         )
            headers = {'content-type': 'application/json'}
            url = self.base_url + '/api/Account/Authenticate'
            r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            return_value = r.json()
            print('Authenticated')
            return return_value['result']

        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

    def get_release_key(self, job_name):

        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.base_url + f'/odata/Releases?$filter=contains(Name, \'{job_name}\')'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}

        r = requests.get(url, headers=headers)
        result = r.json()

        try:
            release_key = result['value'][0]['Key']
        except IndexError:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

        return release_key

    def start_job(self, release_key, inputs):

        """Starts a job with the given release key"""

        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.base_url + '/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = str(
                        {
                            "startInfo": {
                                "ReleaseKey": release_key,
                                "InputArguments": inputs
                               }
                        }
                      )
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 201:
            print('Robot Job has successfully been initiated')
            return True
        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

    def _get_running_job_id(self, release_name):

        """Helper function to get the ID of the running job in question.  This will pass back to the
        job function to Kill the Job"""

        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.base_url + f'/odata/Jobs?$filter=contains(ReleaseName, \'{release_name}\') and State eq \'Running\''
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}

        r = requests.get(url, headers=headers)
        result = r.json()

        if r.status_code == 200:
            try:
                running_job_id = result['value'][0]['Id']

                # Return the Job Id back to the stopJob function
                return running_job_id
            except IndexError:
                raise IndexError('Please make sure the name of the job is correct and the job is running')

        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

    def stop_job(self, release_name):

        """This will hard kill a job that needs to be stopped"""

        if self.token is None:
            raise ValueError("You must authenticate first")

        job_id = self._get_running_job_id(release_name)

        url = self.base_url + f'/odata/Jobs({job_id})/UiPath.Server.Configuration.OData.StopJob'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = str({
                        "strategy": "Kill"
                      })
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            print('robot job has successfully been terminated')
        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

    def start_transaction(self, queue_name):

        """This will start the most recent transaction for this queue.  You can add variables but that has
        not been implemented just yet"""

        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.base_url + '/odata/Queues/UiPathODataSvc.StartTransaction'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = str({
                "transactionData": {
                    "Name": queue_name,
                            }
                       })
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 204:
            print('Transaction has successfully been initiated')
        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

    def create_machine(self, machine_name, description):

        """This will create a machine with the specified parameters"""

        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.base_url + '/odata/Machines'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = str({
                      "Name": machine_name,
                      "Description": description,
                      "Type": "Standard"
                      })
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 201:
            print('Machine has successfully been created')
        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])

    def create_robot(self, machine_name, robot_name, username, password, description,
                     robot_type='Attended', hosting_type='Standard'):

        """This will create a robot with the specified parameters"""

        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.base_url + '/odata/Robots'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = str({
                        "MachineName": machine_name,
                        "Name": robot_name,
                        "Username": username,
                        "Description": description,
                        "Type": robot_type,
                        "HostingType": hosting_type,
                        "Password": password
                      })
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 201:
            print('Robot has successfully been created')
        else:
            raise ValueError("Server Error: " + str(r.status_code) + '.  ' + r.json()['message'])
