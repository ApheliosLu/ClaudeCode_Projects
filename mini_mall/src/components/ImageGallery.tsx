"use client";

import { useState } from "react";

// 简单图片画廊：主图 + 缩略图切换
export function ImageGallery({ images, name }: { images: string[]; name: string }) {
  const [active, setActive] = useState(0);
  const list = images.length > 0 ? images : ["/next.svg"];

  return (
    <div>
      <div className="overflow-hidden rounded-lg border bg-muted">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={list[active]}
          alt={name}
          className="aspect-square w-full object-cover"
        />
      </div>
      {list.length > 1 && (
        <div className="mt-2 flex gap-2">
          {list.map((url, i) => (
            <button
              key={url}
              type="button"
              onClick={() => setActive(i)}
              className={`h-16 w-16 overflow-hidden rounded-md border transition-opacity ${
                i === active ? "ring-2 ring-primary" : "opacity-60 hover:opacity-100"
              }`}
              aria-label={`查看第 ${i + 1} 张图片`}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={url} alt={`${name} ${i + 1}`} className="h-full w-full object-cover" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
