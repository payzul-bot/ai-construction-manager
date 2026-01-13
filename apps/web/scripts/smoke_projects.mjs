import { createProject, deleteProject, listProjects } from "../src/lib/api.js";

const run = async () => {
  const projects = await listProjects();
  const initialCount = Array.isArray(projects) ? projects.length : 0;

  const created = await createProject({
    title: `Smoke Project ${Date.now()}`,
    meta: { source: "smoke" }
  });

  const createdId = created?.id || created?.project_id || created?.data?.id;
  if (!createdId) {
    throw new Error(`Create did not return an id: ${JSON.stringify(created)}`);
  }

  await deleteProject(createdId);

  const updated = await listProjects();
  const updatedCount = Array.isArray(updated) ? updated.length : 0;

  console.log(
    JSON.stringify(
      {
        initialCount,
        updatedCount,
        createdId
      },
      null,
      2
    )
  );
};

run().catch((error) => {
  console.error("Smoke test failed:", error);
  process.exit(1);
});
