# Domain Configuration Guide for ISEE

This guide explains how to use domain-specific configuration files to customize your idea generation process.

## What are Domain-Specific Configuration Files?

Domain-specific configuration files allow you to define custom sets of domains for different scenarios or topics. Instead of being limited to the default domains in the unified configuration, you can create specialized domain sets for particular fields or areas of interest.

## Creating a Domain Configuration File

Domain configuration files are simple JSON files with the following structure:

```json
{
  "domains": [
    {
      "id": "domain_custom_id",
      "name": "Domain Name",
      "description": "A detailed description of the domain and its focus.",
      "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
    },
    {
      "id": "domain_another_id",
      "name": "Another Domain",
      "description": "Description of another domain.",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }
  ]
}
```

### Required Fields

Each domain must have the following fields:

- **id**: A unique identifier for the domain (recommended to start with "domain_")
- **name**: A human-readable name for the domain
- **description**: A detailed description of the domain
- **keywords**: An array of relevant keywords associated with the domain

## Using Domain Configuration Files

To use a domain-specific configuration file:

```bash
python main.py --config unified_config.json --domain-config your_domains.json --query "Your query here"
```

This will load the models, instructions, and other settings from unified_config.json, but will use the domains from your_domains.json instead of the default domains.

## Viewing Available Domains

To list all domains currently available (including domains from a custom configuration file):

```bash
python main.py --config unified_config.json --domain-config your_domains.json --list-domains
```

This will print all domain information including IDs, names, descriptions, and keywords.

## Selecting Specific Domains

Once you've loaded your custom domains, you can still use the `--domain` parameter to run with only specific domains:

```bash
python main.py --config unified_config.json --domain-config your_domains.json --query "Your query" --domain "Domain Name,Another Domain"
```

## Example Domain Configuration Files

The framework comes with several example domain configuration files:

- `tech_writing_domains.json`: Domains focused on technical documentation and content management
- `learning_design_domains.json`: Domains related to instructional design and e-learning

## Best Practices

1. **Be Descriptive**: Provide detailed descriptions that will give the AI models clear context
2. **Include Relevant Keywords**: Add 5-7 keywords that capture the core concepts of the domain
3. **Create Topic-Focused Files**: Group related domains together in a single configuration file
4. **Use Clear Naming**: Give your domains descriptive names and IDs that reflect their content
5. **Test with Dry Run**: Use the `--dry-run` flag to test your domain configurations before executing

## Creating Multiple Domain Sets

You can create as many domain configuration files as needed for different projects or areas of focus. This allows you to quickly switch between different domain contexts without modifying your main configuration file.