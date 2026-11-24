# Taiwan Transfer Pilot MCP

Connect your MCP client to the hosted Taiwan inter-store transfer pilot. Use it
to retrieve historical reports, rerun plans, and open recommendations and weekly
sales audits in Excel.

## Connect your MCP client

The pilot team emails the access token for your brand separately.

1. Add a remote **Streamable HTTP** MCP server in your existing client.
2. Enter `https://ist-tw.sdu-alchemist.org/mcp`.
3. In the client's secure header settings, set `Authorization` to
   `Bearer <your pilot token>`, using the token from your brand’s email.
   Keep the token in your client settings and out of the conversation.
4. Ask your agent:

   > Find my historical pilot workspace and give me the download links for my
   > Phase 3 PDF and workbook.

This setup runs in the hosted service. Participants can connect without
installing Python or cloning the repository. The client must support remote
Streamable HTTP with a custom bearer header. The
[example configuration](mcp.example.json) shows the connection fields.

The agent returns browser links for reports and job files. Each link expires
after 15 minutes. Ask the agent for a fresh link if it expires.

## Workspace examples

Choose the directory for the brand named in your pilot access email.
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
| Inspect and map an approved export | `get_dataset_contracts`, `create_upload`, `get_upload_status`, `inspect_uploaded_data`, `validate_data_mapping`, `save_mapping_version`, `apply_data_mapping` |
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

To upload an approved CSV or Parquet file, have the agent call `create_upload`
in an upload-enabled workspace. Open the returned link, choose the file, and
click **Upload**. Then tell the agent to check `get_upload_status` and review the
data before import. The browser upload accepts files up to 64 MiB.

## Troubleshooting

- **Tools missing.** Verify the `/mcp` URL and select Streamable HTTP in the
  client.
- **Authentication error.** Confirm the client sends the `Authorization` header
  with the token from your brand’s pilot access email.
- **Job pending.** Poll the existing job ID. Use workspace history to find it
  after restarting a session.
- **Link expired.** Request a fresh browser link from the agent.

See [AGENTS.md](AGENTS.md) for the agent workflow and data-handling instructions.
