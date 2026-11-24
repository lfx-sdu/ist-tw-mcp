# Working with the Taiwan Transfer Pilot MCP

Use the configured remote Streamable HTTP server. The generic example names it
`taiwan-transfer-pilot`. The [HTN](examples/htn/README.md),
[APM](examples/apm/README.md), and [ROS](examples/ros/README.md) examples each
provide a separate server entry and historical and synthetic walkthroughs.

The participant receives their brand’s token in a separate email and enters it
in the MCP client’s secure Authorization header.
Keep the credential out of tool arguments, conversation, source files, and reports.
Keep raw uploads and generated files outside version control.

## Discover the workspace and data

1. Call `list_workspaces` and use the workspace the participant selects. A
   workspace defines which profile is used.
2. Use `list_workspace_planning_jobs` to find saved jobs. It returns job IDs,
   data versions, dates, kinds, modes, and statuses. Use `get_planning_job` to
   obtain the full audit or list of downloadable files.
3. For a historical rerun, select the supplied historical pilot workspace, read
   its `head_version_id` with `get_data_version`, and submit the exact
   `source_contract.as_of` date. Use `list_published_files` and
   `download_published_file` for the completed Phase 3 PDF, Phase 3 workbook,
   or archive of as-of planning inputs. The completed research results cover a
   longer period than the first-plan rerun.
4. For a demo rerun, use the baseline version and `as_of` date from the selected
   earlier demo plan or inputs supplied by the participant. A later sales
   version can apply to a weekly audit while the earlier version applies to its
   plan.

## Run a plan and retrieve results

- Discover the supported settings with `get_run_options`. Pass rule overrides
  for Allocation-only runs within the workspace's approved rules.
- Submit `create_planning_job` with the workspace ID, version ID, planning date,
  mode, and idempotency key. Reuse the key for the exact same request after an
  uncertain response. Use a new key for new inputs.
- Poll `get_planning_job` to a terminal status. If the user lost the ID, recover
  it from workspace history. For a successful plan, use the paginated
  `list_planning_recommendations` tool to inspect rows.
- Use `download_planning_artifact` for a file listed on the completed job. Common
  names include `recommendations.xlsx`, `recommendations.csv`, and
  `run_audit.json`. Share the returned browser link and data version with the participant.
  Each link expires after 15 minutes.

## Prepare and upload authorized files

1. Confirm the participant wants the specified files uploaded into the selected
   upload-enabled workspace. Identify the source columns for IDs, dates, quantities,
   and stock or reservations before import.
2. Use `get_dataset_contracts` for accepted names and schemas. Give the participant
   the browser link from `create_upload` and check `get_upload_status` afterward. For unfamiliar exports, use
   `unmapped`, inspect the upload, validate the proposed
   mapping, then save and apply its version. Preserve leading zeroes in codes
   and stable source identifiers. Keep unknown quantities as unresolved.
3. Commit the canonical upload IDs with `import_data_batch`. A baseline imports
   all required datasets and declares coverage. A weekly delta pins the
   expected parent version and covered dates. Declare coverage complete after
   the participant confirms it.
4. If the import reports a conflict or missing coverage, surface it and confirm
   corrections before retrying. Retain the resulting version ID for the plan or
   audit.

## Produce the weekly sales audit

- Find the successful prior-week planning job and the imported sales version.
  Ask for the week if several fit. Pass the Monday as `week_start` and use an
  `as_of` date after that Sunday when the sales version was available.
- Call `create_weekly_audit`, then poll its returned job ID with
  `get_planning_job`. Save `weekly_audit.xlsx` with
  `download_planning_artifact`.
- Describe recommended arrivals and recorded sales in their own units and date
  windows. The workbook compares quantities side by side. Keep causal claims
  about transfers and actual fulfillment outside that comparison.
