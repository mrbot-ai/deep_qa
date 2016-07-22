package org.allenai.semparse.pipeline.science_data

import org.json4s._

import com.mattg.pipeline.Step
import com.mattg.util.FileUtil
import com.mattg.util.JsonHelper

/**
 * This is a grouping of Steps that produce sentences as output.  They can take varying input, but
 * they must produce as output a file that contains one sentence per line, possibly with an index.
 * Output format should be "[sentence]" or "[sentence index][tab][sentence]".
 *
 * This groups together things like SentenceSelector (which takes a corpus as input and finds good
 * sentences to use for training) and SentenceCorrupter (which takes sentences as input and
 * corrupts them to produce negative training data).  The purpose of having this as a superclass is
 * so that things like SentenceToLogic and BackgroundCorpusSearcher don't have to care about
 * whether they are dealing with the output of SentenceSelector or SentenceCorruptor.
 *
 * Note: I originally made this an abstract class, not a trait, so that I could easily access the
 * params and fileUtil from the class.  However, you can only inherit from one class, so
 * SentenceProdcuers couldn't also be SubprocessSteps, which was a problem.  So, at least one of
 * those two has to be a trait, not a class, and this one seemed to make more sense.  This is why
 * this trait has some funny extra defs in here (and why we need a complex return type on
 * SentenceProducer.create).  It is expected that this trait is used in conjunction with a Step,
 * which will already have these values defined.
 */
trait SentenceProducer {
  def params: JValue
  def fileUtil: FileUtil
  val baseParams = Seq("type", "create sentence indices")
  val indexSentences = JsonHelper.extractWithDefault(params, "create sentence indices", false)

  def outputFile: String

  def outputSentences(sentences: Seq[String]) {
    val outputLines = sentences.zipWithIndex.map(sentenceWithIndex => {
      val (sentence, index) = sentenceWithIndex
      if (indexSentences) s"${index}\t${sentence}" else s"${sentence}"
    })
    fileUtil.writeLinesToFile(outputFile, outputLines)
  }
}

object SentenceProducer {
  def create(params: JValue, fileUtil: FileUtil): Step with SentenceProducer = {
    (params \ "type") match {
      case JString("sentence selector") => new SentenceSelectorStep(params, fileUtil)
      case JString("sentence corruptor") => new SentenceCorruptor(params, fileUtil)
      case _ => throw new IllegalStateException("unrecognized SentenceProducer parameters")
    }
  }
}