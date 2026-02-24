import requests


class StarfishClient:
    """HTTP client wraping all Starfish Router API calls."""

    def __init__(self, config: dict):
        self.base_url = config["router_url"]
        self.auth = config["auth"]
        self.site_uid = config["site_uid"]

    def _url(self, path: str) -> str:
        """url full path"""
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: dict = None):
        return requests.get(self._url(path), params=params, auth=self.auth)

    def post(self, path: str, data: dict = None):
        return requests.post(self._url(path), json=data, auth=self.auth)

    def put(self, path: str, data: dict = None):
        return requests.put(self._url(path), json=data, auth=self.auth)

    def delete(self, path: str):
        return requests.delete(self._url(path), auth=self.auth)


    #sites
    def get_site(self):
        """Look up this site by its UID."""
        return self.get("/sites/lookup/", params={"uid": self.site_uid})

    def register_site(self, name: str, description: str):
        """Register this site with the router."""
        return self.post("/sites/", data={
            "uid": self.site_uid,
            "name": name,
            "description": description
        })

    def update_site(self, site_id: int, name: str, description: str):
        """Update site name and description."""
        return self.put(f"/sites/{site_id}/", data={
            "name": name,
            "description": description
        })

    def deregister_site(self, site_id: int):
        """Remove this site from the router."""
        return self.delete(f"/sites/{site_id}/")

    ##projects

    def list_projects(self, site_id: int):
        """List all projects this site is involved in."""
        return self.get("/projects/lookup/", params={"site_id": site_id})

    def get_project(self, project_id: int):
        """Get a single project by ID."""
        return self.get(f"/projects/{project_id}/")

    def create_project(self, name: str, description: str, site_id: int, tasks: list):
        """Create a new project. This site becomes the coordinator."""
        return self.post("/projects/", data={
            "name": name,
            "description": description,
            "site": site_id,
            "tasks": tasks
        })

    def join_project(self, project_name: str, site_id: int, notes: str = ""):
        """Join an existing project as a participant."""
        r = self.get("/projects/lookup/", params={"name": project_name})
        if not r.ok:
            return r
        project = r.json()
        return self.post("/project-participants/", data={
            "site": site_id,
            "project": project["id"],
            "role": "PA",
            "notes": notes if notes else "joining project"
        })

    def leave_project(self, participant_id: int):
        """Leave a project by deleting the participant record."""
        return self.delete(f"/project-participants/{participant_id}/")

    def get_participants(self, project_id: int):
        """Get all participants for a project."""
        return self.get("/project-participants/lookup/", params={"project": project_id})

    #runs

    def start_run(self, project_id: int):
        """Start a new FL run batch. Coordinator only."""
        return self.post("/runs", data={"project": project_id})

    def get_runs(self, project_id: int):
        """Get all runs for a project filtered by this site."""
        return self.get("/runs/lookup/", params={
            "project": project_id,
            "site_uid": self.site_uid
        })

    def get_run_detail(self, batch: int, project_id: int, site_id: int):
        """Get detailed info for a specific run batch."""
        return self.get("/runs/detail/", params={
            "batch": batch,
            "project": project_id,
            "site": site_id
        })

    def update_run_status(self, run_id: int, status: int):
        """Update the status of a run (uses integer status codes 0-8)."""
        return self.put(f"/runs/{run_id}/status/", data={"status": status})

    
    #downlaods

    def download_artifact(self, run_id: int, file_type: str, all_runs: bool = True):
        """Download artifacts or logs as a ZIP file."""
        return self.get("/runs-action/download/", params={
            "run": run_id,
            "type": file_type,
            "all_runs": 1 if all_runs else 0
        })

    def perform_action(self, run_id: int, project_id: int, batch: int, role: str, action: str):
        """Perform a run action: 'stop' or 'restart'."""
        return self.put("/runs-action/update/", data={
            "run": run_id,
            "project": project_id,
            "batch": batch,
            "role": role,
            "action": action
        })