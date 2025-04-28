#!/usr/bin/env python3
"""
Script to generate a secure API key for Tagline backend.
Prints a random URL-safe string to stdout.
"""
import secrets

KEY_LENGTH = 48  # 48 bytes = 64+ chars, URL-safe


def generate_api_key(length=KEY_LENGTH):
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    print(generate_api_key())
