QUERY_SINGLE_TODO = """
query GetTodo($id: String!) {
    todo(id: $id) {
        id
        title
        description
        isCompleted
        createdAt
        dueDate
        priority
        user {
            id
            username
            email
            fullName
        }
        tags {
            id
            name
            color
        }
    }
}
"""
QUERY_PAGINATED_TODOS = """
query GetTodos($pagination: PaginationInput, $filters: FilterInput, $sortBy: String, $order: String) {
    todos(pagination: $pagination, filters: $filters, sortBy: $sortBy, order: $order) {
        page
        size
        totalItems
        totalPages
        items {
            id
            title
            description
            isCompleted
            createdAt
            dueDate
            priority
        }
    }
}
"""

QUERY_NESTED_ENTITIES = """
query GetNestedData($userId: String!) {
    user(id: $userId) {
        id
        username
        email
        fullName
        profile {
            id
            bio
            avatarUrl
            createdAt
            settings {
                theme
                notificationsEnabled
                language
            }
        }
        todos(completed: false) {
            id
            title
            user {
                id
                username
            }
            tags {
                id
                name
                color
            }
        }
    }
}
"""

MUTATION_CREATE_TODO = """
mutation CreateTodo($input: CreateTodoInput!) {
    createTodo(input: $input) {
        id
        title
        description
        isCompleted
        createdAt
        dueDate
        priority
        user {
            id
            username
        }
    }
}
"""

MUTATION_UPDATE_TODO = """
mutation UpdateTodo($id: String!, $input: UpdateTodoInput!) {
    updateTodo(id: $id, input: $input) {
        id
        title
        description
        isCompleted
        updatedAt
        dueDate
        priority
    }
}
"""

MUTATION_DELETE_TODO = """
mutation DeleteTodo($id: String!) {
    deleteTodo(id: $id)
}
"""


SUBSCRIPTION_TODO_EVENTS = """
subscription TodoEvents($eventTypes: [String!]) {
    todoEvents(eventTypes: $eventTypes) {
        id
        eventType
        payload
        createdAt
    }
}
"""


SAMPLE_VARIABLES = {
    "pagination_vars": {
        "pagination": {
            "page": 1,
            "size": 10
        },
        "filters": {
            "completed": False,
            "priority": ["HIGH", "MEDIUM"]
        },
        "sortBy": "created_at",
        "order": "desc"
    },
    
    "create_todo_vars": {
        "input": {
            "title": "Learn GraphQL Federation",
            "description": "Implement Level 3 GraphQL federation for microservices",
            "dueDate": "2024-12-31",
            "priority": "HIGH"
        }
    },
    
    "update_todo_vars": {
        "id": "todo-id-here",
        "input": {
            "isCompleted": True,
            "priority": "LOW"
        }
    },
    
    "subscription_vars": {
        "eventTypes": ["TODO_CREATED", "TODO_UPDATED", "TODO_DELETED"]
    }
}


CURL_EXAMPLES = """
# Test GraphQL Query
curl -X POST http://localhost:8000/graphql \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "query { todos(pagination: {page: 1, size: 5}) { page totalItems items { id title isCompleted } } }"
  }'

# Test GraphQL Mutation
curl -X POST http://localhost:8000/graphql \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "mutation CreateTodo($input: CreateTodoInput!) { createTodo(input: $input) { id title createdAt } }",
    "variables": {
      "input": {
        "title": "Test TODO from cURL",
        "description": "Testing GraphQL API",
        "priority": "MEDIUM"
      }
    }
  }'
"""

if __name__ == "__main__":
    print("GraphQL TODO API Demo")
    print("====================")
    print()
    print("Features implemented:")
    print("✅ Level 1: Related entities (Todo, User)")
    print("✅ Level 2: Nested entities with depth > 2 (Todo -> User -> Profile -> Settings)")
    print("✅ Level 3: GraphQL Subscriptions for events")
    print("✅ Mutations for CRUD operations")
    print("✅ Pagination support")
    print("✅ DataLoader pattern for N+1 optimization")
    print()
    print("To start the server:")
    print("python graphql_server.py")
    print()
    print("Then visit: http://localhost:8000/graphql")
    print("For GraphiQL interface to test queries interactively")
    print()
    print("Sample queries available in this file:")
    print("- QUERY_SINGLE_TODO")
    print("- QUERY_PAGINATED_TODOS") 
    print("- QUERY_NESTED_ENTITIES")
    print("- MUTATION_CREATE_TODO")
    print("- MUTATION_UPDATE_TODO")
    print("- MUTATION_DELETE_TODO")
    print("- SUBSCRIPTION_TODO_EVENTS")
