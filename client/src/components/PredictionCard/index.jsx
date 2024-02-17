import {CheckCircle2} from 'lucide-react'
import clsx from 'clsx'

const PredictionCard = ({statement, prediction, isLoading}) => {
  const colorClass = () => {
    if (isLoading) {
      return 'bg-secondary-base'
    }
    if (prediction === 1) {
      return 'bg-primary-base'
    }
    return 'bg-tertiary-base'
  }
  return (
    <div className="w-full flex flex-col px-4 py-3 gap-2 bg-white rounded-3xl">
      <div className="w-full flex flex-row px-0 py-1 gap-4 items-center">
        <div className={clsx("flex p-2 items-center rounded-xl", colorClass())}>
          <CheckCircle2 color="#ffffff" className='w-6 h-6' />
        </div>
        <p className='font-normal text-text text-body.base'>{statement}</p>
      </div>
      <div className='flex flex-row self-start px-4 py-2 rounded-full bg-[#EFF2F8]'>
        {prediction === 1 ? (
          <p className='text-primary-base'>Not offensive</p>
        ) : (
          <p className='text-tertiary-base'>Offensive</p>
        )}
      </div>
    </div>
  )
}

export default PredictionCard