import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Header() {
  return (
    <nav className="sticky top-0 z-50 bg-background/80 backdrop-blur-lg border-b">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="text-xl font-bold">
            师承×学成
          </Link>
          <div className="flex gap-4">
            <Button variant="ghost" asChild>
              <Link href="/about">关于我们</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/creator">我是创作者</Link>
            </Button>
            <Button variant="ghost" asChild>
              <Link href="/learner">我是学习者</Link>
            </Button>
          </div>
        </div>
      </div>
    </nav>
  )
}