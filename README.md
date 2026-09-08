# CRIMINAL INTELLIGENCE ANALYSIS SYSTEM

AI-powered investigative intelligence analysis system developed as a prototype for **Smart India Hackathon 2026**.

## Problem Statement

**SIH26189 — AI-Powered Criminal Network Analysis System**

The system is designed to analyze fragmented investigative data and help investigators identify entities, relationships, network structures, and analytical patterns.

## Overview

Investigative information can be distributed across multiple sources such as:

- FIR records
- Call Detail Records (CDR)
- Financial transactions
- Surveillance reports
- Social media intelligence
- Criminal history
- Intelligence reports

This prototype brings synthetic investigation data into a unified analytical interface.

It extracts and organizes entities such as:

- People
- Phone numbers
- Vehicles
- Locations
- Organizations
- Email addresses

The system then maps relationships between entities and provides analytical insights to support investigation.

## Key Features

### Entity Extraction
Extracts relevant entities from investigative text.

### Entity Intelligence
Provides structured information about individual entities, including entity type, connections, and analytical priority.

### Entity Resolution
Helps consolidate references that may represent the same underlying entity.

### Network Analysis
Visualizes relationships between entities using an interactive network graph.

### Evidence-Linked Relationships
Associates observed relationships with supporting evidence and source information.

### Phone Intelligence
Provides synthetic phone-number metadata and network-level analytical indicators.

### Investigation Dashboard
Provides an overview of entities, relationships, and investigation signals.

### Report Generation
Generates structured analytical reports for different investigation views.

## Technology Stack

- Python
- Streamlit
- Pandas
- NetworkX
- Plotly

## System Architecture

Investigative Data
        ↓
Entity Extraction
        ↓
Entity Resolution
        ↓
Relationship Analysis
        ↓
Network Construction
        ↓
Graph Analysis
        ↓
Investigator Dashboard
        ↓
Analytical Reports
