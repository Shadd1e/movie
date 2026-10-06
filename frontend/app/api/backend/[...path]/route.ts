import { NextRequest, NextResponse } from "next/server"

const backendUrl = process.env.NEXT_PUBLIC_API_URL

async function proxy(request: NextRequest, path: string[]) {
  if (!backendUrl) {
    return NextResponse.json(
      { detail: "NEXT_PUBLIC_API_URL is not configured." },
      { status: 500 },
    )
  }

  const base = backendUrl.replace(/\/$/, "")

  const target =
    `${base}/${path.map(encodeURIComponent).join("/")}` +
    request.nextUrl.search

  const headers = new Headers()

  const authorization = request.headers.get("authorization")
  const contentType = request.headers.get("content-type")

  if (authorization) {
    headers.set("Authorization", authorization)
  }

  if (contentType) {
    headers.set("Content-Type", contentType)
  }

  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.arrayBuffer()

  const response = await fetch(target, {
    method: request.method,
    headers,
    body,
    cache: "no-store",
  })

  const responseHeaders = new Headers()

  const responseContentType = response.headers.get("content-type")

  if (responseContentType) {
    responseHeaders.set("Content-Type", responseContentType)
  }

  return new NextResponse(response.body, {
    status: response.status,
    headers: responseHeaders,
  })
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params
  return proxy(request, path)
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params
  return proxy(request, path)
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params
  return proxy(request, path)
}

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params
  return proxy(request, path)
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params
  return proxy(request, path)
}