## Description

TodoList is a task management API. It lets you add, list, remove and update tasks

## Endpoints
`GET /tasks` - Retrirve all tasks
`GET /tasks/:id` - Get a task with the specified id
`POST /tasks` - Create a new task
`PUT /tasks/:id` - Update the task with the specified id
`DELETE /tasks/:id` - Remove the task with the id

###  Installation & Usage
You need to have uv installed
1. **Clone the Repo**
```bash
git clone https://github.com/TodoList
cd TodoList
```

2. **Install Requirements**
```bash
uv add
```

3. **Run the project**
You can run the project using
```bash
uv run fastapi dev
```

or

```bash
uv run main.py
```

## Example

![Development](image.png)
![curl request](image2.png)
![swagger](image3.png)