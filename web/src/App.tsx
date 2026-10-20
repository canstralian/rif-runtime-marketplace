import React, { useState } from "react";
import {
  Shield, Search, Compass, Bookmark, ArrowUpRight, ArrowRight, Terminal,
  Crosshair, FileCode2, Network, Bot, LockKeyhole, Layers, Check, BookOpen,
  type LucideIcon,
} from "lucide-react";
import { Button, Input, Dialog, DialogContent, DialogTitle, DialogDescription } from "./ui";
import s from "./App.module.css";

type Plugin = {
  id: string;
  name: string;
  category: string;
  icon: LucideIcon;
  desc: string;
  tags: string[];
  permissions: string[];
  workflow: string;
  version: string;
};

const plugins: Plugin[] = [
  {
    id: "scope", name: "Scopekeeper", category: "Red teaming", icon: Crosshair,
    desc: "Turn rules of engagement into explicit boundaries for every assessment.",
    tags: ["Scope validation", "Guardrails"],
    permissions: ["Read assessment scope files", "Write local validation reports"],
    workflow: "Import a synthetic rules-of-engagement document, review scope boundaries, and inspect a proposed assessment plan.",
    version: "0.4.2",
  },
  {
    id: "audit", name: "Code Sentry", category: "App security", icon: FileCode2,
    desc: "A second set of eyes for insecure patterns, dependencies, and risky code changes.",
    tags: ["Code review", "SAST"],
    permissions: ["Read selected repository files", "Write local findings"],
    workflow: "Select a local repository snapshot and review evidence-linked findings before accepting any proposed change.",
    version: "1.2.0",
  },
  {
    id: "trace", name: "Trace Atlas", category: "Recon & OSINT", icon: Network,
    desc: "Connect public-source evidence into a clear, traceable research workspace.",
    tags: ["Evidence mapping", "OSINT"],
    permissions: ["Read imported evidence", "Write local research graph"],
    workflow: "Import public-source research fixtures and trace every relationship to its source.",
    version: "0.8.1",
  },
  {
    id: "agent", name: "Agent Boundary", category: "AI security", icon: Bot,
    desc: "Explore prompt injection scenarios and inspect tool authority in a contained lab.",
    tags: ["Agent testing", "Prompt injection"],
    permissions: ["Read synthetic test fixtures", "Write local test results"],
    workflow: "Run through a simulated injection test plan and inspect proposed tool calls. No real tools are executed.",
    version: "0.3.0",
  },
  {
    id: "report", name: "Finding Studio", category: "Reporting", icon: BookOpen,
    desc: "Shape raw observations into consistent, evidence-first security reports.",
    tags: ["Reporting", "Evidence"],
    permissions: ["Read selected finding files", "Write report drafts"],
    workflow: "Review synthetic findings and assemble a report draft with reproduction context and remediation notes.",
    version: "1.0.3",
  },
  {
    id: "config", name: "Config Lens", category: "App security", icon: LockKeyhole,
    desc: "Make configuration drift and exposed defaults easier to spot before release.",
    tags: ["Configuration", "Hardening"],
    permissions: ["Read selected configuration files", "Write local review notes"],
    workflow: "Import fixture configuration files and inspect a proposed hardening checklist.",
    version: "0.6.1",
  },
];

const categories = ["All plugins", "Red teaming", "App security", "Recon & OSINT", "AI security", "Reporting"] as const;
const categoryIcons: Record<string, LucideIcon> = {
  "Red teaming": Crosshair,
  "App security": FileCode2,
  "Recon & OSINT": Network,
  "AI security": Bot,
  Reporting: BookOpen,
};

function readBookmarks(): string[] {
  try {
    const raw: unknown = JSON.parse(localStorage.getItem("forge-saved") ?? "[]");
    return Array.isArray(raw)
      ? raw.filter((id): id is string => typeof id === "string" && plugins.some((p) => p.id === id))
      : [];
  } catch {
    return [];
  }
}

export default function App() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("All plugins");
  const [view, setView] = useState<"discover" | "saved">("discover");
  const [detail, setDetail] = useState<Plugin | null>(null);
  const [about, setAbout] = useState(false);
  const [notice, setNotice] = useState("");
  const [saved, setSaved] = useState<string[]>(readBookmarks);

  function toggle(id: string) {
    const next = saved.includes(id) ? saved.filter((x) => x !== id) : [...saved, id];
    setSaved(next);
    try {
      localStorage.setItem("forge-saved", JSON.stringify(next));
      setNotice("");
    } catch {
      setNotice("Saved for this visit. Browser storage is unavailable.");
    }
  }

  const normalized = query.trim().toLocaleLowerCase();
  const visible = plugins.filter((p) =>
    (view !== "saved" || saved.includes(p.id)) &&
    (category === "All plugins" || p.category === category) &&
    [p.name, p.desc, p.category, ...p.tags].join(" ").toLocaleLowerCase().includes(normalized)
  );

  function navigate(next: "discover" | "saved") {
    setView(next);
    setCategory("All plugins");
    setQuery("");
  }

  return (
    <div className={s.app}>
      <aside className={s.sidebar}>
        <a className={s.brand} href={import.meta.env.BASE_URL} aria-label="Forge Exchange home">
          <span className={s.brandIcon}><Shield size={23} /></span>
          <span>forge<span className={s.brandSub}>EXCHANGE</span></span>
        </a>
        <div className={s.workspace}><span className={s.dot} /> CLAUDE PLUGIN DIRECTORY</div>
        <nav className={s.nav} aria-label="Main navigation">
          <Button variant="ghost" className={view === "discover" ? s.active : s.navButton} onClick={() => navigate("discover")}>
            <Compass size={18} /> Discover <span>↗</span>
          </Button>
          <Button variant="ghost" className={view === "saved" ? s.active : s.navButton} onClick={() => navigate("saved")}>
            <Bookmark size={18} /> My collection <span>{saved.length}</span>
          </Button>
        </nav>
        <p className={s.navLabel}>EXPLORE BY DISCIPLINE</p>
        <div className={s.categoryNav}>
          {categories.slice(1).map((name) => {
            const Icon = categoryIcons[name];
            return (
              <Button key={name} variant="ghost" className={category === name ? s.active : s.navButton}
                onClick={() => { setView("discover"); setCategory(name); }}>
                <Icon size={17} /> {name}
              </Button>
            );
          })}
        </div>
        <div className={s.sidebarBottom}>
          <div className={s.lab}>
            <Shield size={21} />
            <strong>Built for responsible work.</strong>
            <p>Know the scope. Inspect permissions. Keep a human in control.</p>
            <Button variant="link" onClick={() => setAbout(true)}>Our directory principles <ArrowUpRight size={14} /></Button>
          </div>
          <div className={s.profile}><span>F</span><div>Forge workspace<small>Prototype edition</small></div></div>
        </div>
      </aside>

      <div className={s.body}>
        <header className={s.topbar}>
          <span>Marketplace <span className={s.slash}>/</span> <strong>{view === "saved" ? "My collection" : "Discover"}</strong></span>
          <Button variant="outline" size="sm" onClick={() => setAbout(true)}><Terminal size={15} /> How it works</Button>
        </header>
        <main className={s.main}>
          <div className={s.eyebrow}><span className={s.dot} /> THE SECURITY OPERATOR’S TOOLKIT</div>
          <section className={s.hero}>
            <div>
              <h1>{view === "saved" ? "Your tools.\nYour collection." : <>Extend Claude.<br /><span>Sharpen your edge.</span></>}</h1>
              <p>Discover purpose-built plugins for security research,<br className={s.desktopBreak} /> authorised red teaming, and better defensive workflows.</p>
            </div>
            <div className={s.heroArt} aria-hidden="true">
              <div className={s.orbit} /><div className={s.orbitTwo} />
              <div className={s.core}><Shield size={64} strokeWidth={1} /></div>
              <span className={s.artTag}><Terminal size={14} /> skills + tools + context</span>
            </div>
          </section>
          <div className={s.demo}><span>DEMO DIRECTORY</span> All listings are fictional concepts. No plugins are installed or executed.</div>

          {view === "discover" && category === "All plugins" && !query && (
            <section className={s.featured}>
              <div>
                <div className={s.featureLabel}><Layers size={15} /> FEATURED WORKFLOW</div>
                <h2>Good assessments start<br />with clear boundaries.</h2>
                <p>Explore Scopekeeper: scope first, evidence throughout.</p>
                <Button onClick={() => setDetail(plugins[0])}>Explore plugin <ArrowRight size={16} /></Button>
              </div>
              <div className={s.terminal} aria-label="Illustrative terminal">
                <div className={s.terminalTop}><i /><i /><i /><span>scopekeeper / preview</span></div>
                <p><span>01</span> engagement.load("lab-scope.json")</p>
                <p><span>02</span> authority: <b>explicit</b></p>
                <p><span>03</span> targets: <b>allowlisted</b></p>
                <p><span>04</span> external_execution: <b>disabled</b></p>
                <div className={s.terminalFoot}><Check size={14} /> Boundaries before capabilities.</div>
              </div>
            </section>
          )}

          <section className={s.catalog}>
            <div className={s.catalogHeading}>
              <div><h2>{view === "saved" ? "My collection" : "Explore the directory"}</h2>
                <p>{view === "saved" ? "Your saved shortlist, stored in this browser." : "Find the right capability for your next engagement."}</p></div>
              <span className={s.count}>{visible.length} plugins</span>
            </div>
            <div className={s.search}>
              <Search size={18} />
              <Input aria-label="Search plugins" placeholder="Search plugins, capabilities, or workflows…" value={query} onChange={(e) => setQuery(e.target.value)} />
              <span>SEARCH</span>
            </div>
            <div className={s.filters} aria-label="Filter by category">
              {categories.map((name) => <Button size="sm" variant={category === name ? "secondary" : "ghost"} key={name}
                className={category === name ? s.selectedFilter : ""} aria-pressed={category === name}
                onClick={() => setCategory(name)}>{name}</Button>)}
            </div>

            {notice && <p role="status">{notice}</p>}
            <div className={s.grid}>
              {visible.map((p) => {
                const Icon = p.icon;
                return (
                  <article className={s.card} key={p.id}>
                    <div className={s.cardTop}>
                      <span className={s.pluginIcon}><Icon size={25} /></span>
                      <Button variant="ghost" size="icon-sm"
                        aria-label={saved.includes(p.id) ? "Remove " + p.name + " from collection" : "Save " + p.name}
                        aria-pressed={saved.includes(p.id)} onClick={() => toggle(p.id)}>
                        <Bookmark size={18} fill={saved.includes(p.id) ? "currentColor" : "none"} />
                      </Button>
                    </div>
                    <div className={s.cardCategory}>{p.category}</div>
                    <h3>{p.name}</h3>
                    <p>{p.desc}</p>
                    <div className={s.tags}>{p.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
                    <div className={s.cardFooter}><span>CONCEPT · v{p.version}</span>
                      <Button variant="ghost" size="sm" onClick={() => setDetail(p)}>View plugin <ArrowUpRight size={15} /></Button>
                    </div>
                  </article>
                );
              })}
            </div>
            {visible.length === 0 && (
              <div className={s.empty}>
                <Search size={30} />
                <h3>{view === "saved" && !saved.length ? "Your collection starts here." : "No matching plugins."}</h3>
                <p>{view === "saved" && !saved.length
                  ? "Save plugins using the bookmark icon to build your shortlist."
                  : "Try a different search or clear your category filter."}</p>
                <Button variant="outline" onClick={() => navigate("discover")}>Browse all plugins</Button>
              </div>
            )}
          </section>
          <footer className={s.footer}>
            <span>FORGE EXCHANGE <span> / </span> Tools with boundaries.</span>
            <span>Independent prototype · Not affiliated with Anthropic</span>
          </footer>
        </main>
      </div>

      <Dialog open={!!detail} onOpenChange={(open) => { if (!open) setDetail(null); }}>
        <DialogContent className={s.dialog}>
          {detail && <>
            <div className={s.eyebrow}>FICTIONAL PLUGIN CONCEPT · v{detail.version}</div>
            <DialogTitle className={s.dialogTitle}>{detail.name}</DialogTitle>
            <DialogDescription>{detail.desc}</DialogDescription>
            <h3>Example workflow</h3><p>{detail.workflow}</p>
            <h3>Proposed permissions</h3>
            <ul>{detail.permissions.map((p) => <li key={p}>{p}</li>)}</ul>
            <div className={s.permissionNote}><Shield size={18} />
              <span>Not security reviewed. Permissions are illustrative; no repository, compatibility, or publisher has been verified. Installation is unavailable in this prototype.</span>
            </div>
            <Button onClick={() => toggle(detail.id)}><Bookmark size={16} />
              {saved.includes(detail.id) ? "Remove from collection" : "Save to collection"}
            </Button>
          </>}
        </DialogContent>
      </Dialog>
      <Dialog open={about} onOpenChange={setAbout}>
        <DialogContent className={s.dialog}>
          <DialogTitle>Capabilities with clear boundaries.</DialogTitle>
          <DialogDescription>Forge Exchange is a discovery prototype for a Claude plugin marketplace.</DialogDescription>
          <h3>1. Discover</h3><p>Search six fictional plugin concepts and filter by security discipline.</p>
          <h3>2. Inspect</h3><p>Review the intended workflow and proposed permissions. A listing is not a security endorsement.</p>
          <h3>3. Collect</h3><p>Save a shortlist in this browser. Nothing is installed, downloaded, or executed.</p>
          <div className={s.permissionNote}>Production listings would need source provenance, pinned versions, compatibility checks, and a documented review process.</div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
