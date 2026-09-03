# Third-party notices

## Bundled community plugins

The ICOR for Life Scaffold bundles two unmodified community plugins for
Obsidian so the vault works out of the box. They are separate works by
their own authors, distributed under their own licenses, aggregated
here for convenience:

| Plugin | Author | Version bundled | License | Source |
| --- | --- | --- | --- | --- |
| Terminal | polyipseity | 3.27.1 | AGPL-3.0 | https://github.com/polyipseity/obsidian-terminal |
| Outliner | Viacheslav Slinko | 4.10.2 | MIT | https://github.com/vslinko/obsidian-outliner |

Full license texts ship inside each plugin's folder under
`.obsidian/plugins/`. The complete corresponding source code of each
plugin is available at the linked repositories.

These plugins are listed in Obsidian's official community catalog.
After first open, run Settings -> Community plugins -> Check for
updates to move to the latest official versions; Obsidian's updater
recognizes the bundled copies normally.

## Components inside the ICOR plugins

The ICOR plugins are our own work. Several of them bundle no
third-party code at all: ICOR Focus, ICOR Interface and myICOR Connect are
hand-written JavaScript against the Obsidian plugin API.

**ICOR Planner** embeds the source-tool glyphs (Todoist, ClickUp) as SVG
path data from the Simple Icons project (https://simpleicons.org),
released under CC0 1.0 Universal. The brand marks themselves remain
subject to their owners' trademark policies.

**ICOR Chat** bundles the Claude Agent SDK for TypeScript
(`@anthropic-ai/claude-agent-sdk`), published by Anthropic, version
0.3.226, from https://github.com/anthropics/claude-agent-sdk-typescript.
The SDK is not open source. Its package declares its license as "SEE
LICENSE IN README.md", and that README places use of the SDK under
Anthropic's Commercial Terms of Service, at
https://www.anthropic.com/legal/commercial-terms.

The Claude Code binary is NOT bundled or redistributed. ICOR Chat runs the
copy of Claude Code already installed on your own machine, unmodified, and
you sign in to it with your own Anthropic account through Anthropic's own
sign-in flow. The plugin never collects, stores, or relays your
credentials, and your Claude usage is billed to you under your own
agreement with Anthropic. myICOR is not affiliated with, endorsed by, or
partnered with Anthropic.

Two open-source libraries are bundled alongside the SDK. Their notices
follow in full:

  Zod - MIT License - https://github.com/colinhacks/zod

    Copyright (c) 2020 Colin McDonnell

    Permission is hereby granted, free of charge, to any person obtaining
    a copy of this software and associated documentation files (the
    "Software"), to deal in the Software without restriction, including
    without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to
    the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
    BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

  OpenTelemetry API for JavaScript - Apache License 2.0 -
  https://github.com/open-telemetry/opentelemetry-js

    Copyright The OpenTelemetry Authors

    Licensed under the Apache License, Version 2.0 (the "License"); you
    may not use this file except in compliance with the License. You may
    obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
    implied. See the License for the specific language governing
    permissions and limitations under the License.

    This library is redistributed unmodified.

**ICOR SQLite Viewer** bundles sql.js (a WebAssembly build of SQLite,
MIT License, https://github.com/sql-js/sql.js) as its mobile and
fallback engine; SQLite itself is public domain. The full notice ships
in the plugin's own `THIRD-PARTY-NOTICES.md`. The desktop engine is the
`sqlite3` command line tool already on the member's machine, which is
not bundled or redistributed.

No copyleft-licensed code (GPL, LGPL, AGPL or MPL) is bundled inside any
ICOR plugin. The only copyleft component in this vault is the Terminal
community plugin listed above, which ships unmodified and separate.

Obsidian itself is NOT bundled or redistributed; users install it from
obsidian.md under Obsidian's own terms.
