name: Documentation fix
about: To add, correct or remove something from the documentation
title: ''
labels: documentation
assignees: ''
body:
  - type: dropdown
    id: action
    attributes:
      label: Type of action
      description: "What do you want to do: remove something, add it, or change it?"
      options:
        - Remove
        - Add
        - Change
      default: 1
    validations:
      required: true
  - type: textarea
    id: where
    attributes:
      label: Where?
      description: Specify which part of the documentation you want to make a change to?
      placeholder: For example, the name of an existing documentation section or the line number in a file README.md
    validations:
      required: true
  - type: textarea
    id: essence
    attributes:
      label: The essence
      placeholder: Please describe the essence of the proposed change
      render: shell
    validations:
      required: true