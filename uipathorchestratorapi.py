import requests


class uipathConnection:
    def __init__(self, url, tenant, username, password):
        self.tenant = tenant
        self.username = username
        self.password = password
        self.baseurl = url
        self.token = None

    def authenticate(self):
        payload = str({"tenancyName": self.tenant, "usernameOrEmailAddress": self.username, "password": self.password})
        headers = {'content-type': 'application/json'}
        url = self.baseurl + '/api/Account/Authenticate'
        r = requests.post(url, data=payload, headers=headers)

        if r.status_code == 200:
            return_value = r.json()
            self.token = return_value['result']
            print('Authenticated')
        else:
            print(r.status_code)
            raise ValueError(
                "Please check the connection string and try again"
            )

    def getReleaseKey(self, jobname):

        if self.token is None:
            raise ValueError ("You must authenticate first")


        url = self.baseurl + f'/odata/Releases?$filter=contains(Name, \'{jobname}\')'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}

        r = requests.get(url, headers=headers)

        result = r.json()
        try:
            releaseKey = result['value'][0]['Key']
        except:
            raise ValueError("Please check the robot name and try again")


        return releaseKey

    def startJob(self, releasekey):
        if self.token is None:
            raise ValueError("You must authenticate first")

        url = self.baseurl + '/odata/Jobs/UiPath.Server.Configuration.OData.StartJobs'
        headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = str({
                  "startInfo": {
                    "ReleaseKey": releasekey
                        }
                  })
        r = requests.post(url, data=payload, headers=headers)

        result = r.json()
        if r.status_code == 201:
            print('robot has successfully been initiated')
        else:
            raise ValueError("Server Error: " + str(r.status_code) + ". Please check the payload and try again")