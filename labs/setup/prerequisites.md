# Lab Prerequisites — Tools & Versions

These labs are full-stack: a PostgreSQL database, three interchangeable
backends (.NET, Python, and Java/Spring Boot — you run **one**), and a React
frontend. Install the tools below once; every module reuses them.

They run on **macOS, Linux, and Windows**. Throughout the labs, shell snippets
are given twice where the platforms differ:

- **macOS / Linux** — bash or zsh
- **Windows** — PowerShell (works in Windows Terminal, VS Code, or the
  standalone PowerShell app). If you prefer **WSL2**, follow the macOS / Linux
  instructions inside your Linux distribution instead.

## Required

| Tool | Version | Check | Used by |
|------|---------|-------|---------|
| Git | 2.40+ | `git --version` | everything |
| PostgreSQL | 15 or 16 | `psql --version` | all backends (local install **or** Docker) |
| Node.js | 20 LTS or newer | `node --version` | React (Vite) frontend |
| npm | 10+ | `npm --version` | ships with Node |
| .NET SDK | 8.0.x | `dotnet --version` | .NET backend + xUnit tests |
| Python | 3.11–3.14 | `python3 --version` (Windows: `python --version`) | FastAPI backend + pytest |
| Java (JDK) | 21 LTS | `java -version` | Java backend + JUnit tests |
| Maven | 3.9+ | `mvn -version` | building the Java backend |

You only need the toolchain for the **one backend you choose to run**. Install
all three if you want to try the Exercise 3 "port it to another language" step.

## Optional but recommended

| Tool | Why |
|------|-----|
| Docker Desktop | Run PostgreSQL without a local install; used from Module 03 onward |
| VS Code + GitHub Copilot | The programme's primary AI pair-programming surface |
| `curl` or a REST client (Bruno / Postman) | Exercising API endpoints by hand (`curl` ships with macOS, modern Linux, and Windows 10+) |

## Installing the toolchain

### macOS (Homebrew)

```bash
brew install git node python@3.12 openjdk@21 maven postgresql@16
brew install --cask dotnet-sdk
brew install --cask docker            # optional

# make the JDK visible to /usr/bin/java
sudo ln -sfn $(brew --prefix)/opt/openjdk@21/libexec/openjdk.jdk \
  /Library/Java/JavaVirtualMachines/openjdk-21.jdk
```

### Linux (Debian / Ubuntu)

```bash
sudo apt update
sudo apt install -y git curl postgresql-16 openjdk-21-jdk maven
# Node 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs
# .NET 8 SDK
sudo apt install -y dotnet-sdk-8.0
```

(Fedora/RHEL: swap `apt` for `dnf` and the package names accordingly.)

### Windows (winget, in an elevated PowerShell)

```powershell
winget install --id Git.Git -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.12 -e
winget install --id Microsoft.OpenJDK.21 -e
winget install --id Apache.Maven -e
winget install --id Microsoft.DotNet.SDK.8 -e
winget install --id PostgreSQL.PostgreSQL.16 -e
winget install --id Docker.DockerDesktop -e   # optional
```

After installing, **close and reopen your terminal** so `PATH` updates. If
`psql` or `mvn` is still "not recognized", add its `bin` folder to `PATH`
(PostgreSQL: `C:\Program Files\PostgreSQL\16\bin`; Maven: the `bin` under where
winget placed it) via *Settings → System → About → Advanced system settings →
Environment Variables*.

## GitHub Copilot (course-wide)

Module 01 is context-setting and does not require Copilot to be active, but you
will use it from Module 02 on. Confirm now that:

- You are signed in to GitHub in your IDE.
- Your organisation has enabled **GitHub Copilot Enterprise** for your account.
- Copilot Chat is available in the IDE side panel.

## Next

- [Database setup](database-setup.md)
- Backend setup (pick one): [.NET](dotnet-setup.md) · [Python](python-setup.md) · [Java](java-setup.md)
- [GitHub Spec Kit setup](speckit-setup.md) — needed from Module 04 on
