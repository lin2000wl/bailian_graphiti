"""
Copyright 2024, Zep Software, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from typing import Any, Protocol, TypedDict

from pydantic import BaseModel, Field, model_validator, ConfigDict

from .models import Message, PromptFunction, PromptVersion


class ExtractedEntity(BaseModel):
    name: str = Field(..., description='Name of the extracted entity')
    entity_type_id: int = Field(
        description='ID of the classified entity type. '
        'Must be one of the provided entity_type_id integers.',
    )


class ExtractedEntities(BaseModel):
    extracted_entities: list[ExtractedEntity] = Field(..., description='List of extracted entities')

    @model_validator(mode='before')
    @classmethod
    def handle_entities_field(cls, values):
        # Handle case where API returns a list directly instead of an object
        if isinstance(values, list):
            # Process each entity in the list to handle entity_name -> name mapping
            processed_entities = []
            for entity in values:
                if isinstance(entity, dict):
                    entity = entity.copy()
                    # Handle entity_name -> name mapping
                    if 'entity_name' in entity and 'name' not in entity:
                        entity['name'] = entity['entity_name']
                        del entity['entity_name']
                processed_entities.append(entity)
            return {'extracted_entities': processed_entities}
        
        if isinstance(values, dict):
            # Handle different field names from different APIs
            if 'entities' in values and 'extracted_entities' not in values:
                values = values.copy()
                values['extracted_entities'] = values['entities']
                del values['entities']
            
            # Handle case where the entire response is a list under a different key
            if len(values) == 1 and isinstance(list(values.values())[0], list):
                key = list(values.keys())[0]
                if key != 'extracted_entities':
                    values = {'extracted_entities': values[key]}
            
            # Process entities within the extracted_entities list
            if 'extracted_entities' in values and isinstance(values['extracted_entities'], list):
                processed_entities = []
                for entity in values['extracted_entities']:
                    if isinstance(entity, dict):
                        entity = entity.copy()
                        # Handle entity_name -> name mapping
                        if 'entity_name' in entity and 'name' not in entity:
                            entity['name'] = entity['entity_name']
                            del entity['entity_name']
                    processed_entities.append(entity)
                values['extracted_entities'] = processed_entities
            
            # Handle case where there's no extracted_entities key but there are entities
            if 'extracted_entities' not in values:
                # Look for any key that contains a list of entities
                for key, value in values.items():
                    if isinstance(value, list) and len(value) > 0:
                        # Check if this looks like a list of entities
                        if isinstance(value[0], dict) and ('name' in value[0] or 'entity_name' in value[0]):
                            processed_entities = []
                            for entity in value:
                                if isinstance(entity, dict):
                                    entity = entity.copy()
                                    # Handle entity_name -> name mapping
                                    if 'entity_name' in entity and 'name' not in entity:
                                        entity['name'] = entity['entity_name']
                                        del entity['entity_name']
                                processed_entities.append(entity)
                            values = {'extracted_entities': processed_entities}
                            break
        
        return values


class MissedEntities(BaseModel):
    missed_entities: list[str] = Field(..., description="Names of entities that weren't extracted")


class EntityClassificationTriple(BaseModel):
    uuid: str = Field(description='UUID of the entity')
    name: str = Field(description='Name of the entity')
    entity_type: str | None = Field(
        default=None, description='Type of the entity. Must be one of the provided types or None'
    )


class EntityClassification(BaseModel):
    entity_classifications: list[EntityClassificationTriple] = Field(
        ..., description='List of entities classification triples.'
    )


class Prompt(Protocol):
    extract_message: PromptVersion
    extract_json: PromptVersion
    extract_text: PromptVersion
    reflexion: PromptVersion
    classify_nodes: PromptVersion
    extract_attributes: PromptVersion


class Versions(TypedDict):
    extract_message: PromptFunction
    extract_json: PromptFunction
    extract_text: PromptFunction
    reflexion: PromptFunction
    classify_nodes: PromptFunction
    extract_attributes: PromptFunction


def extract_message(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that extracts entity nodes from conversational messages. 
    Your primary task is to extract and classify the speaker and other significant entities mentioned in the conversation.
    Please respond in JSON format with the extracted entities. Always use valid JSON structure in your response."""

    user_prompt = f"""
<PREVIOUS MESSAGES>
{json.dumps([ep for ep in context['previous_episodes']], indent=2)}
</PREVIOUS MESSAGES>

<CURRENT MESSAGE>
{context['episode_content']}
</CURRENT MESSAGE>

<ENTITY TYPES>
{context['entity_types']}
</ENTITY TYPES>

Instructions:

You are given a conversation context and a CURRENT MESSAGE. Your task is to extract **entity nodes** mentioned **explicitly or implicitly** in the CURRENT MESSAGE.
Pronoun references such as he/she/they or this/that/those should be disambiguated to the names of the 
reference entities.

1. **Speaker Extraction**: Always extract the speaker (the part before the colon `:` in each dialogue line) as the first entity node.
   - If the speaker is mentioned again in the message, treat both mentions as a **single entity**.

2. **Entity Identification**:
   - Extract all significant entities, concepts, or actors that are **explicitly or implicitly** mentioned in the CURRENT MESSAGE.
   - **Exclude** entities mentioned only in the PREVIOUS MESSAGES (they are for context only).

3. **Entity Classification**:
   - Use the descriptions in ENTITY TYPES to classify each extracted entity.
   - Assign the appropriate `entity_type_id` for each one.

4. **Exclusions**:
   - Do NOT extract entities representing relationships or actions.
   - Do NOT extract dates, times, or other temporal information—these will be handled separately.

5. **Formatting**:
   - Be **explicit and unambiguous** in naming entities (e.g., use full names when available).

{context['custom_prompt']}

Please respond in JSON format with the extracted entities. Use a valid JSON structure with the following format:
{{"extracted_entities": [{{"name": "entity_name", "entity_type_id": 0}}]}}
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def extract_json(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that extracts entity nodes from JSON. 
    Your primary task is to extract and classify relevant entities from JSON files.
    Please respond in JSON format with the extracted entities. Always use valid JSON structure in your response."""

    user_prompt = f"""
<SOURCE DESCRIPTION>:
{context['source_description']}
</SOURCE DESCRIPTION>
<JSON>
{context['episode_content']}
</JSON>
<ENTITY TYPES>
{context['entity_types']}
</ENTITY TYPES>

{context['custom_prompt']}

Given the above source description and JSON, extract relevant entities from the provided JSON.
For each entity extracted, also determine its entity type based on the provided ENTITY TYPES and their descriptions.
Indicate the classified entity type by providing its entity_type_id.

Guidelines:
1. Always try to extract an entities that the JSON represents. This will often be something like a "name" or "user field
2. Do NOT extract any properties that contain dates

Please respond in JSON format with the extracted entities. Use a valid JSON structure with the following format:
{{"extracted_entities": [{{"name": "entity_name", "entity_type_id": 0}}]}}
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def extract_text(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that extracts entity nodes from text. 
    Your primary task is to extract and classify the speaker and other significant entities mentioned in the provided text.
    Please respond in JSON format with the extracted entities. Always use valid JSON structure in your response."""

    user_prompt = f"""
<TEXT>
{context['episode_content']}
</TEXT>
<ENTITY TYPES>
{context['entity_types']}
</ENTITY TYPES>

Given the above text, extract entities from the TEXT that are explicitly or implicitly mentioned.
For each entity extracted, also determine its entity type based on the provided ENTITY TYPES and their descriptions.
Indicate the classified entity type by providing its entity_type_id.

{context['custom_prompt']}

Guidelines:
1. Extract significant entities, concepts, or actors mentioned in the conversation.
2. Avoid creating nodes for relationships or actions.
3. Avoid creating nodes for temporal information like dates, times or years (these will be added to edges later).
4. Be as explicit as possible in your node names, using full names and avoiding abbreviations.

Please respond in JSON format with the extracted entities. Use a valid JSON structure with the following format:
{{"extracted_entities": [{{"name": "entity_name", "entity_type_id": 0}}]}}
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def reflexion(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that determines which entities have not been extracted from the given context. 
    Please respond in JSON format with the missed entities."""

    user_prompt = f"""
<PREVIOUS MESSAGES>
{json.dumps([ep for ep in context['previous_episodes']], indent=2)}
</PREVIOUS MESSAGES>
<CURRENT MESSAGE>
{context['episode_content']}
</CURRENT MESSAGE>

<EXTRACTED ENTITIES>
{context['extracted_entities']}
</EXTRACTED ENTITIES>

Given the above previous messages, current message, and list of extracted entities; determine if any entities haven't been
extracted.

Please respond in JSON format with the missed entities.
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def classify_nodes(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are an AI assistant that classifies entity nodes given the context from which they were extracted.
    Please respond in JSON format with the entity classifications."""

    user_prompt = f"""
    <PREVIOUS MESSAGES>
    {json.dumps([ep for ep in context['previous_episodes']], indent=2)}
    </PREVIOUS MESSAGES>
    <CURRENT MESSAGE>
    {context['episode_content']}
    </CURRENT MESSAGE>
    
    <EXTRACTED ENTITIES>
    {context['extracted_entities']}
    </EXTRACTED ENTITIES>
    
    <ENTITY TYPES>
    {context['entity_types']}
    </ENTITY TYPES>
    
    Given the above conversation, extracted entities, and provided entity types and their descriptions, classify the extracted entities.
    
    Guidelines:
    1. Each entity must have exactly one type
    2. Only use the provided ENTITY TYPES as types, do not use additional types to classify entities.
    3. If none of the provided entity types accurately classify an extracted node, the type should be set to None
    
    Please respond in JSON format with the entity classifications.
"""
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]


def extract_attributes(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are a helpful assistant that extracts entity properties from the provided text.',
        ),
        Message(
            role='user',
            content=f"""

        <MESSAGES>
        {json.dumps(context['previous_episodes'], indent=2)}
        {json.dumps(context['episode_content'], indent=2)}
        </MESSAGES>

        Given the above MESSAGES and the following ENTITY, update any of its attributes based on the information provided
        in MESSAGES. Use the provided attribute descriptions to better understand how each attribute should be determined.

        Guidelines:
        1. Do not hallucinate entity property values if they cannot be found in the current context.
        2. Only use the provided MESSAGES and ENTITY to set attribute values.
        3. The summary attribute represents a summary of the ENTITY, and should be updated with new information about the Entity from the MESSAGES. 
            Summaries must be no longer than 250 words.
        
        <ENTITY>
        {context['node']}
        </ENTITY>
        """,
        ),
    ]


versions: Versions = {
    'extract_message': extract_message,
    'extract_json': extract_json,
    'extract_text': extract_text,
    'reflexion': reflexion,
    'classify_nodes': classify_nodes,
    'extract_attributes': extract_attributes,
}
