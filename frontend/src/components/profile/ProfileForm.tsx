"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useProfileStore } from "@/store/profileStore";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";

export function ProfileForm() {
  const { profile, loading, error, fetchProfile, updateProfile } = useProfileStore();
  const [fullName, setFullName] = useState("");
  const [profilePicture, setProfilePicture] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  useEffect(() => {
    if (profile) {
      setFullName(profile.full_name ?? "");
      setProfilePicture(profile.profile_picture ?? "");
    }
  }, [profile]);

  async function handleSave() {
    setSaving(true);
    try {
      await updateProfile({ full_name: fullName, profile_picture: profilePicture });
      toast.success("Profile updated");
    } catch {
      toast.error("Couldn't update profile");
    } finally {
      setSaving(false);
    }
  }

  if (loading && !profile) {
    return <p className="text-sm text-ink/60">Loading profile…</p>;
  }

  return (
    <Card className="max-w-lg space-y-4">
      {error && <p className="text-sm text-danger">{error}</p>}

      <div>
        <label className="mb-1 block text-sm font-medium">Email</label>
        <Input value={profile?.email ?? ""} disabled />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Full name</label>
        <Input
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          placeholder="Your name"
        />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium">Profile picture URL</label>
        <Input
          value={profilePicture}
          onChange={(e) => setProfilePicture(e.target.value)}
          placeholder="https://…"
        />
      </div>

      <Button onClick={handleSave} disabled={saving}>
        {saving ? "Saving…" : "Save changes"}
      </Button>
    </Card>
  );
}