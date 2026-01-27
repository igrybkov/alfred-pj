#!/usr/bin/env python3
# encoding: utf-8
"""Entry point for Alfred workflow. Delegates to the alfred_pj CLI."""

from alfred_pj.cli import cli

if __name__ == '__main__':
    cli()
