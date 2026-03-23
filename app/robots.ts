import { MetadataRoute } from "next";

const APP_URL = "https://uchide-kozuchi.vercel.app";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: "/",
      disallow: "/api/",
    },
    sitemap: `${APP_URL}/sitemap.xml`,
  };
}
