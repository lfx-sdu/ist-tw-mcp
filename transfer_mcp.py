"""Per-customer MCP stdio tools using the same authenticated HTTP API."""
import base64,json,os
from contextlib import asynccontextmanager
import hashlib
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated,Literal
from urllib.parse import urlsplit

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import Field


ResourceId = Annotated[str, Field(pattern=r'^[a-f0-9]{32}$')]
PageLimit = Annotated[int, Field(ge=1, le=500)]
PageOffset = Annotated[int, Field(ge=0)]
PlanningArtifact = Literal['recommendations.xlsx','recommendations.csv','run_audit.json',
                           'shipments.csv','brief.md','issues.csv','weekly_audit.xlsx']


def create_mcp(api_url,api_token,*,client=None,max_file_bytes=8*1024*1024,download_dir=None):
    if not api_token:raise ValueError('customer API credential required for MCP')
    server=FastMCP('Inter-store Transfer',instructions='Upload baseline or incremental files, run planning, review recommendations and save plan files locally. All tools use the customer API identity. Uploads use bounded base64 content or registered upload IDs.')
    headers = {'Authorization': 'Bearer ' + api_token}
    download_root = Path(download_dir).expanduser().resolve() if download_dir else None

    @asynccontextmanager
    async def api_session():
        if client is not None:
            yield client
        else:
            async with httpx.AsyncClient(base_url=api_url, timeout=60) as session:
                yield session

    async def call(method,path,payload=None,content=None):
        async with api_session() as session:
            response=await session.request(method,path,json=payload,content=content,headers=headers)
            if response.status_code>=400:
                message=response.json().get('detail','API request failed')
                raise ValueError(str(message))
            return response.json()
    @server.tool()
    async def list_profiles()->dict:
        """List available reference profiles and their validation qualification."""
        return {'profiles':await call('GET','/v1/profiles')}
    @server.tool()
    async def get_run_options()->dict:
        """Inspect full/allocation-only run options and supported rule combination schema."""
        return await call('GET','/v1/run-options')
    @server.tool()
    async def get_dataset_contracts()->dict:
        """Inspect required canonical fields, stable identities and declarative mapping schema."""
        return await call('GET','/v1/dataset-contracts')
    @server.tool()
    async def inspect_uploaded_data(upload_id:str)->dict:
        """Inspect bounded samples/quality and advisory candidates; confirm actual field meanings."""
        return await call('GET','/v1/uploads/'+upload_id+'/inspection')
    @server.tool()
    async def validate_data_mapping(upload_id:str,definition:dict,context:dict|None=None,base_version_id:str|None=None)->dict:
        """Validate every transformed row without publishing data or guessing units/dates."""
        return await call('POST','/v1/mappings/validate',dict(upload_id=upload_id,definition=definition,context=context,base_version_id=base_version_id))
    @server.tool()
    async def save_mapping_version(workspace_id:str,upload_id:str,definition:dict,idempotency_key:str,
        context:dict|None=None,base_version_id:str|None=None,parent_id:str|None=None)->dict:
        """Save a checked immutable mapping; updates name the current parent version."""
        return await call('POST','/v1/workspaces/'+workspace_id+'/mappings',dict(upload_id=upload_id,definition=definition,
            idempotency_key=idempotency_key,context=context,base_version_id=base_version_id,parent_id=parent_id))
    @server.tool()
    async def get_mapping_version(mapping_id:str)->dict:
        """Read a customer's versioned mapping definition and validation provenance."""
        return await call('GET','/v1/mappings/'+mapping_id)
    @server.tool()
    async def apply_data_mapping(mapping_id:str,upload_id:str,idempotency_key:str,context:dict|None=None,base_version_id:str|None=None)->dict:
        """Produce a new canonical upload, retaining the raw file and mapping/parent identity."""
        return await call('POST','/v1/mappings/'+mapping_id+'/apply',dict(upload_id=upload_id,idempotency_key=idempotency_key,
            context=context,base_version_id=base_version_id))
    @server.tool()
    async def get_profile_template(workspace_id:str)->dict:
        """Examine actual reference business rules and their qualification before drafting."""
        return await call('GET','/v1/workspaces/'+workspace_id+'/profile-template')
    @server.tool()
    async def create_profile_draft(workspace_id:str,name:str,idempotency_key:str,mapping_ids:dict|None=None,
        business_rules:dict|None=None,allocation_rules:dict|None=None,rules_confirmed:bool=False,notes:str='',parent_id:str|None=None)->dict:
        """Record a profile proposal/confirmation; unsupported rule changes remain review-required."""
        return await call('POST','/v1/workspaces/'+workspace_id+'/profile-drafts',dict(name=name,idempotency_key=idempotency_key,
            mapping_ids=mapping_ids or {},business_rules=business_rules or {},allocation_rules=allocation_rules,
            rules_confirmed=rules_confirmed,notes=notes,parent_id=parent_id))
    @server.tool()
    async def get_profile_draft(profile_draft_id:str)->dict:
        """Read immutable customer rule/mapping/configuration proposals."""
        return await call('GET','/v1/profile-drafts/'+profile_draft_id)
    @server.tool()
    async def validate_profile_draft(profile_draft_id:str)->dict:
        """List unanswered questions, adapter-review changes and data/model readiness."""
        return await call('POST','/v1/profile-drafts/'+profile_draft_id+'/validate')
    @server.tool()
    async def preview_profile_draft(profile_draft_id:str,version_id:str,as_of:str,idempotency_key:str)->dict:
        """Queue allocation-only preview of a confirmed compatible draft and mapped data version."""
        return await call('POST','/v1/profile-drafts/'+profile_draft_id+'/preview',dict(version_id=version_id,as_of=as_of,idempotency_key=idempotency_key))
    @server.tool()
    async def get_active_profile(workspace_id:str)->dict:
        """Read the active customer profile and whether its review remains current."""
        return await call('GET','/v1/workspaces/'+workspace_id+'/active-profile')
    @server.tool()
    async def list_customer_profile_versions(workspace_id:str)->dict:
        """Read immutable approved versions available for comparison or rollback."""
        return await call('GET','/v1/workspaces/'+workspace_id+'/customer-profiles')
    @server.tool()
    async def create_workspace(name:str,profile_id:str)->dict:
        """Create a customer workspace bound to a reference profile."""
        return await call('POST','/v1/workspaces',dict(name=name,profile_id=profile_id))

    @server.tool()
    async def list_workspaces(limit: PageLimit = 20, offset: PageOffset = 0) -> dict:
        """Find workspace IDs by listing the workspaces available to this account."""
        return await call('GET', f'/v1/workspaces?limit={limit}&offset={offset}')

    @server.tool()
    async def create_upload(workspace_id:str,dataset:str,format:str,filename:str)->dict:
        """Register an upload slot; binary clients use its authenticated content endpoint."""
        return await call('POST','/v1/uploads',dict(workspace_id=workspace_id,dataset=dataset,format=format,filename=filename))
    @server.tool()
    async def upload_data_file(workspace_id:str,dataset:str,format:str,filename:str,content_base64:str)->dict:
        """Upload a baseline or weekly delta file, bounded to 8 MiB decoded."""
        if len(content_base64)>4*((max_file_bytes+2)//3):raise ValueError('MCP file exceeds size limit; use the binary upload API')
        try:data=base64.b64decode(content_base64,validate=True)
        except ValueError:raise ValueError('file content must be valid base64') from None
        if len(data)>max_file_bytes:raise ValueError('MCP file exceeds size limit')
        slot=await call('POST','/v1/uploads',dict(workspace_id=workspace_id,dataset=dataset,format=format,filename=filename))
        return await call('PUT',slot['content_endpoint'],content=data)
    @server.tool()
    async def import_data_batch(workspace_id:str,kind:str,idempotency_key:str,uploads:list[dict],source_contract:dict|None=None,
        base_version_id:str|None=None,period_start:str|None=None,period_end:str|None=None,coverage:dict|None=None)->dict:
        """Atomically commit a baseline or explicit delta batch against its expected parent."""
        data=dict(workspace_id=workspace_id,kind=kind,idempotency_key=idempotency_key,uploads=uploads,
            source_contract=source_contract,base_version_id=base_version_id,period_start=period_start,period_end=period_end,coverage=coverage)
        return await call('POST','/v1/imports',{k:v for k,v in data.items() if v is not None})
    @server.tool()
    async def get_data_version(version_id:str)->dict:
        """Inspect immutable data version and source declarations."""
        return await call('GET','/v1/data-versions/'+version_id)
    @server.tool()
    async def create_planning_job(workspace_id:str,version_id:str,as_of:str,idempotency_key:str,
        run_type:Literal['full','allocation_only']='full',allocation_rules:dict|None=None,profile_draft_id:str|None=None,active_profile_id:str|None=None)->dict:
        """Queue a full ML+feedback+consolidation run or a pure allocation rule scenario."""
        return await call('POST','/v1/planning-jobs',dict(workspace_id=workspace_id,version_id=version_id,as_of=as_of,
            idempotency_key=idempotency_key,run_type=run_type,allocation_rules=allocation_rules,profile_draft_id=profile_draft_id,active_profile_id=active_profile_id))
    @server.tool()
    async def get_planning_job(job_id:str)->dict:
        """Read job status and, once complete, the run audit and available files."""
        return await call('GET','/v1/planning-jobs/'+job_id)

    @server.tool()
    async def create_weekly_audit(workspace_id: ResourceId, planning_job_id: ResourceId,
                                  sales_version_id: ResourceId, week_start: str, as_of: str,
                                  idempotency_key: str) -> dict:
        """Queue an Excel comparison of the prior week's plan and recorded sales for a closed Monday–Sunday week."""
        return await call('POST', f'/v1/workspaces/{workspace_id}/weekly-audit-jobs',
                          dict(planning_job_id=planning_job_id, sales_version_id=sales_version_id,
                               week_start=week_start, as_of=as_of, idempotency_key=idempotency_key))

    @server.tool()
    async def list_workspace_planning_jobs(workspace_id: ResourceId, limit: PageLimit = 10,
                                           offset: PageOffset = 0) -> dict:
        """Find job IDs in workspace history, newest first, with each job's status, mode and planning date."""
        page = await call('GET', f'/v1/workspaces/{workspace_id}/planning-jobs?limit={limit}&offset={offset}')
        fields = ('id', 'kind', 'status', 'run_type', 'as_of', 'version_id')
        page['items'] = [{field: job[field] for field in fields} for job in page['items']]
        return page

    @server.tool()
    async def list_planning_recommendations(job_id: ResourceId, limit: PageLimit = 50,
                                           offset: PageOffset = 0) -> dict:
        """Read a page of recommendation rows from a completed planning job."""
        return await call('GET', f'/v1/planning-jobs/{job_id}/recommendations?limit={limit}&offset={offset}')

    @server.tool()
    async def download_planning_artifact(job_id: ResourceId, artifact_name: PlanningArtifact) -> dict:
        """Save a completed planning or weekly-audit file locally and return its path."""
        if download_root is None:
            raise ValueError('Set TRANSFER_MCP_DOWNLOAD_DIR in the local MCP launcher to save files.')
        job = await get_planning_job(job_id)
        if job['status'] != 'succeeded':
            raise ValueError('A successful planning job is required.')
        artifact = next((entry for entry in job['result']['artifacts'] if entry['name'] == artifact_name), None)
        if artifact is None:
            raise ValueError('The requested file is unavailable for this job.')

        saved = await save_file(f"/v1/artifacts/{artifact['id']}", f'{job_id}-{artifact_name}')
        return dict(job_id=job_id, name=artifact_name, **saved)

    @server.tool()
    async def list_published_files(workspace_id: ResourceId) -> dict:
        """List the historical PDF, workbook and dated rerun inputs assigned to this workspace."""
        return await call('GET', f'/v1/workspaces/{workspace_id}/published-files')

    @server.tool()
    async def download_published_file(workspace_id: ResourceId, file_id: ResourceId) -> dict:
        """Verify and save a published historical file in the configured local downloads directory."""
        if download_root is None:
            raise ValueError('Set TRANSFER_MCP_DOWNLOAD_DIR in the local MCP launcher to save files.')
        catalogue = await list_published_files(workspace_id)
        file = next((entry for entry in catalogue['files'] if entry['id'] == file_id), None)
        if file is None:
            raise ValueError('The requested file is unavailable in this workspace.')
        name = file['name']
        if not re.fullmatch(r'[A-Za-z0-9_.-]{1,160}', name):
            raise ValueError('Invalid published filename.')
        saved = await save_file(f'/v1/published-files/{file_id}', f'{file_id}-{name}', expected=file)
        return dict(file_id=file_id, name=name, **saved)

    async def save_file(endpoint, filename, expected=None):
        destination = download_root / filename
        temporary_path = None
        checksum = hashlib.sha256()
        try:
            async with api_session() as session:
                async with session.stream('GET', endpoint, headers=headers, follow_redirects=False) as response:
                    response.raise_for_status()
                    download_root.mkdir(mode=0o700, parents=True, exist_ok=True)
                    with NamedTemporaryFile(dir=download_root, prefix='.download-', delete=False) as temporary:
                        temporary_path = Path(temporary.name)
                        async for chunk in response.aiter_bytes():
                            if expected:
                                if temporary.tell() + len(chunk) > expected['size_bytes']:
                                    raise ValueError('Published file exceeds its declared size.')
                                checksum.update(chunk)
                            temporary.write(chunk)
                        size = temporary.tell()
            if expected and (size != expected['size_bytes'] or checksum.hexdigest() != expected['sha256']):
                raise ValueError('Published file integrity check failed.')
            os.replace(temporary_path, destination)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        return dict(path=str(destination), size_bytes=size)

    return server



def main():
    url = os.environ.get('TRANSFER_API_URL', 'https://ist-tw.sdu-alchemist.org')
    origin = urlsplit(url)
    if (origin.scheme != 'https' or not origin.hostname or origin.username is not None
            or origin.password is not None or origin.path not in ('', '/') or origin.query or origin.fragment):
        raise SystemExit('TRANSFER_API_URL must be an HTTPS API origin.')

    token = os.environ.get('TRANSFER_API_TOKEN')
    token_file = os.environ.get('TRANSFER_API_TOKEN_FILE')
    if not token and token_file:
        try:
            token = Path(token_file).expanduser().read_text(encoding='utf-8').strip()
        except (OSError, UnicodeError):
            raise SystemExit('Could not read TRANSFER_API_TOKEN_FILE.') from None
    if not token:
        raise SystemExit('Set TRANSFER_API_TOKEN_FILE or TRANSFER_API_TOKEN with your pilot credential.')

    server = create_mcp(url, token, download_dir=os.environ.get('TRANSFER_MCP_DOWNLOAD_DIR'))
    server.run(transport='stdio')


if __name__ == '__main__':
    main()
