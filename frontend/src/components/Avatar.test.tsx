import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { Avatar } from "./avatars";

test("Avatar renders SVG when no imageUrl", () => {
  render(<Avatar id="fox" size={48} title="Zorro" />);
  expect(screen.getByRole("img", { name: "Zorro" })).toBeInTheDocument();
});

test("Avatar renders img tag when imageUrl provided", () => {
  render(<Avatar id="fox" imageUrl="/media/avatars/1.png" title="custom" size={80} />);
  const img = screen.getByRole("img", { name: "custom" });
  expect(img.tagName).toBe("IMG");
  expect((img as HTMLImageElement).src).toContain("/media/avatars/1.png");
});
