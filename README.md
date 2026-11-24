# Taiwan Transfer Pilot MCP

Connect a local MCP client to the Taiwan inter-store transfer pilot. Participants
can download their historical reports and planning inputs, rerun a plan,
find past jobs, and save recommendations and weekly sales audits as Excel files.

API base URL: `https://ist-tw.sdu-alchemist.org`

The MCP adapter runs as a local stdio process and calls the API over HTTPS.

## Connect your MCP client

You need Python 3.12, a client that supports local stdio MCP, and a tenant token
issued by the pilot operator.

1. Clone the repository and install the client.

   ```sh
   git clone https://github.com/lfx-sdu/ist-tw-mcp.git
   cd ist-tw-mcp
   python3.12 -m venv .venv
   .venv/bin/python -m pip install -r requirements.txt
   ```

   On Windows, use `py -3.12 -m venv .venv` and
   `.venv\Scripts\python.exe -m pip install -r requirements.txt`. Use that
   executable in the following step.

2. Save the token in a private text file outside the repository and restrict it
   to your account. On macOS or Linux, set its permissions to `600`. The file
   should contain the token alone. A client with secure environment settings can
   supply `TRANSFER_API_TOKEN` directly.

3. Add the server entry from [mcp.example.json](mcp.example.json) to your client's
   local MCP settings. Replace the executable, script, token file, and download
   directory with absolute paths. The download directory is created when needed.
   Reload the MCP client.

4. Ask your agent:

   > Find my historical pilot workspace. List and save my Phase 3 PDF and
   > workbook. Run a Full plan using the workspace's historical inputs and
   > save the new recommendations workbook when it succeeds.

If you have a saved audit job, ask the agent to recover it from workspace
history and save `weekly_audit.xlsx`. The tool returns a path on your computer.

## Workspace examples

Choose the directory that matches the tenant token issued by the pilot operator.
Each example includes MCP settings, a first-plan historical rerun, and a
synthetic walkthrough.

| Workspace | Example |
| --- | --- |
| HTN | [Rerun the first plan and compare planning modes](examples/htn/README.md) |
| APM | [Rerun the first plan and recover the sample weekly sales audit](examples/apm/README.md) |
| ROS | [Rerun the first plan and preview a piece cap](examples/ros/README.md) |

## Common workflows

| What you want to do | MCP tools |
| --- | --- |
| Find your workspace or recover a job ID | `list_workspaces`, `list_workspace_planning_jobs` |
| Get the Phase 3 PDF, workbook or historical input archive | `list_published_files`, `download_published_file` |
| Review a profile or preview rule changes | `get_profile_template`, `create_profile_draft`, `validate_profile_draft`, `preview_profile_draft` |
| Run a plan | `get_data_version`, `get_run_options`, `create_planning_job`, `get_planning_job` |
| Review recommendations or save the result | `list_planning_recommendations`, `download_planning_artifact` |
| Inspect and map an approved export | `get_dataset_contracts`, `upload_data_file`, `inspect_uploaded_data`, `validate_data_mapping`, `save_mapping_version`, `apply_data_mapping` |
| Commit baseline inputs or weekly changes | `import_data_batch` |
| Compare a prior plan with the completed week's sales | `create_weekly_audit`, `get_planning_job`, `download_planning_artifact` |

**Full** uses the workspace's assigned planning profile and frozen models for the
selected version. **Allocation-only** supports scenarios with limits such as
maximum pieces, additional source reserves, and route exclusions. Ask the agent
to check the available options before submitting a run.

The historical workspace starts with a fixed data version. Call
`get_data_version` using the workspace's `head_version_id` and use its
`source_contract.as_of` for a rerun. **Full** uses the sealed historical forecast
scores and reruns planning. **Allocation-only** uses historical sales and stock.
The Phase 3 files contain the completed multiweek study. The input archive
covers its first decision date. Use a separate workspace to upload new data.

A new weekly sales audit uses a successful prior-week plan and a version with
complete recorded sales for the reviewed Monday–Sunday week. It compares
recommendations due to arrive during that week with gross sales, returns, and
net sales for the receiving store and SKU.

Pilot workspaces may contain synthetic demo data. Confirm the workspace and
approval to upload before sending actual exports. The upload tool accepts up to
8 MiB of decoded CSV or Parquet content. For larger files, use the authenticated
binary upload API after creating an upload slot.

## Troubleshooting

- **Tools missing.** Reload the MCP client and verify the absolute paths in its
  configuration.
- **Authentication error.** Check the token file and confirm the pilot operator
  issued that token for your tenant.
- **Job pending.** Poll the existing job ID and use workspace history if the
  session was restarted.
- **Download unavailable.** Check the requested file in the workspace catalogue
  or completed job. Confirm your download directory is writable.

See [AGENTS.md](AGENTS.md) for the agent workflow and data-handling instructions.
