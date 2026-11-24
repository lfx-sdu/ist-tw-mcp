# APM workspace example

Use the APM tenant token and the settings in [mcp.example.json](mcp.example.json).
Follow the [client setup](../../README.md#connect-your-mcp-client) to install the
shared adapter and fill in the absolute paths. The MCP server entry is
`taiwan-transfer-pilot-apm`.

## Recover the weekly sales audit

Ask your agent:

> Open my APM pilot demo workspace. Find the latest successful weekly sales
> audit for May 4 through May 10, 2026. Save the Excel workbook and tell me
> how many pieces were recommended and how many net sales pieces were recorded.

The agent can follow these steps:

1. Call `list_workspaces` and select **APM pilot demo (synthetic)**. Its
   assigned profile is `apm_tw`. Use the returned workspace ID.
2. Call `list_workspace_planning_jobs` and look for a successful job with
   `kind: weekly_audit`. Use `get_planning_job` to confirm the audited week
   and identify the saved plan and sales version used.
3. Call `download_planning_artifact` with the **audit job's ID** and the
   filename `weekly_audit.xlsx`. Return the saved file path.
4. Use the workbook's **Receiver sales** sheet to compare recommended pieces
   with gross sales, returns, and net sales by receiving store and SKU.
   **Summary** records the dates and the two input versions.

The worksheet compares synthetic recommendations with synthetic sales for the
week. Its sales counts include all recorded sales for those receiver and SKU
pairs within the week.
