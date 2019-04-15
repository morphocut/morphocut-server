<template>
  <div class="project">
    <div v-if="title">
      <vue-headful v-if="title" title="Tasks | MorphoCut"/>
    </div>
    <div style="margin-top: 1rem; margin-bottom: 1rem;" v-if="title">
      <h2 id="project-title" class="project-title">
        <b-badge>{{title}}</b-badge>
      </h2>
      <div class="project-divider"></div>
    </div>
    <div class="row" :key="getAction">
      <div class="col-6">
        <h4 id="tasks-title" class="tasks-title">
          <b>Running Tasks:</b>
        </h4>
        <table class="table table-hover table-sm">
          <thead class="thead-light">
            <tr>
              <th scope="col" v-if="showProject">Project</th>
              <th scope="col">Status</th>
              <th scope="col">Started At</th>
              <th scope="col">Progress</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(task, index) in running_tasks" :key="index">
              <th scope="col" v-if="showProject">{{task.project_name}}</th>
              <td>{{ task.status }}</td>
              <td>{{ task.started_at }}</td>
              <td>
                <b-progress>
                  <b-progress-bar :value="task.progress">
                    <strong>{{ task.progress.toFixed(0) }}%</strong>
                  </b-progress-bar>
                </b-progress>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="col-6">
        <h4 id="tasks-title" class="tasks-title">
          <b>Finished Tasks:</b>
        </h4>
        <table class="table table-hover table-sm">
          <thead class="thead-light">
            <tr>
              <th scope="col" v-if="showProject">Project</th>
              <th scope="col">Status</th>
              <!-- <th scope="col">Complete</th> -->
              <th scope="col">Download</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(task, index) in finished_tasks" :key="index">
              <th scope="col" v-if="showProject">{{task.project_name}}</th>
              <td>{{ task.status }}</td>
              <!-- <td>{{ task.complete }}</td> -->
              <td>
                <b-button
                  variant="success"
                  size="sm"
                  style="margin-left: 0.5rem;"
                  v-if="task.download_path"
                  :href="task.download_path"
                >Download</b-button>
              </td>
              <td>
                <b-button
                  variant="danger"
                  size="sm"
                  style="margin-left: 0.5rem;"
                  v-on:click="removeTask(task.id)"
                >Delete</b-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
<style>
.tasks .tasks-title {
  margin-bottom: 0.3rem;
  text-align: left;
}

.tasks .tasks-divider {
  height: 1px;
  background: darkgrey;
}

.tasks .tasks-image {
  max-width: 100%;
  max-height: 100%;
}

.tasks {
  margin-left: 2rem;
  margin-right: 2rem;
}
</style>

<script>
import axios from "axios";
export default {
  data() {
    return {
      running_tasks: [],
      finished_tasks: []
    };
  },
  props: {
    getAction: null,
    title: null,
    showProject: false
  },
  methods: {
    getTaskStatus() {
      const path = this.getAction;
      console.log("get task status: " + this.getAction);

      axios.get(path).then(res => {
        this.finished_tasks = res.data.finished_tasks;
        this.running_tasks = res.data.running_tasks;
        console.log(res);

        var unfinished_task = false;

        this.running_tasks.forEach(element => {
          if (element.complete === false && element.status != "failed") {
            unfinished_task = true;
          }
        });

        if (!unfinished_task) {
          return false;
        }

        setTimeout(
          function() {
            this.getTaskStatus();
          }.bind(this),
          2000
        );
      });
    },
    removeTask(task_id) {
      const path = "/api/jobs/" + task_id + "/remove";
      axios.get(path).then(res => {
        this.getTaskStatus();
      });
    }
  },
  created() {
    this.getTaskStatus();
  }
};
</script>